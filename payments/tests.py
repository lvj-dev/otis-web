from decimal import Decimal

from core.factories import SemesterFactory, UserFactory
from core.models import Semester
from django.conf import settings
from django.contrib.auth.models import User
from evans_django_tools.testsuite import EvanTestCase
from roster.factories import InvoiceFactory, StudentFactory
from roster.models import Student

from payments.factories import JobFactory, JobFolderFactory, PaymentLogFactory, WorkerFactory  # NOQA
from payments.models import Job, PaymentLog, Worker, get_semester_invoices_with_annotations  # NOQA

from .views import process_payment


class PaymentTest(EvanTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.alice = StudentFactory.create(user__username='alice')
        cls.invoice = InvoiceFactory.create(student=cls.alice)
        cls.checksum = cls.alice.get_checksum(settings.INVOICE_HASH_KEY)

    def test_invoice_standalone(self):
        self.assertGetDenied('payments-invoice', PaymentTest.alice.pk, '?')
        self.login(PaymentTest.alice)
        self.assertGetDenied('payments-invoice', PaymentTest.alice.pk, '?')
        str(PaymentTest.invoice)  # make sure __str__ is alive
        self.assertGet20X('payments-invoice', self.alice.pk, PaymentTest.checksum)

        bob = StudentFactory.create(user__username='bob')
        self.assertGetNotFound('payments-invoice', bob.pk,
                                bob.get_checksum(settings.INVOICE_HASH_KEY))

    def test_config(self):
        self.assertPost40X('payments-config')
        resp = self.assertGet20X('payments-config')
        self.assertIn('publicKey', resp.json())

    def test_checkout(self):
        pk = PaymentTest.invoice.pk
        self.assertPost40X('payments-checkout', pk, 240)
        self.assertGet40X('payments-checkout', pk, 0)  # amount >= 0

        if settings.STRIPE_PUBLISHABLE_KEY:
            resp = self.assertGet20X('payments-checkout', pk, 480)
            self.assertIn('sessionId', resp.json())

    def test_process_payment(self):
        process_payment(300, PaymentTest.invoice)
        self.assertEqual(PaymentTest.invoice.total_owed, 180)
        log = PaymentLog.objects.get()
        self.assertEqual(log.invoice.pk, PaymentTest.invoice.pk)
        self.assertEqual(log.amount, 300)

    def test_webhook(self):
        self.assertGet40X('payments-webhook')
        self.assertPost40X('payments-webhook')
        self.assertPost40X('payments-webhook', HTTP_STRIPE_SIGNATURE="meow")

    def test_success(self):
        self.assertGet20X('payments-success')

    def test_cancelled(self):
        self.assertGet20X('payments-cancelled')


class WorkerTest(EvanTestCase):

    def test_worker(self) -> None:
        alice: User = UserFactory.create(username='alice')
        self.login(alice)

        resp = self.assertPostOK(
            'worker-update',
            data={
                'gmail_address': 'alice.aardvark@gmail.com',
                'notes': 'hi there'
            },
            follow=True)
        self.assertContains(resp, 'alice.aardvark@gmail.com')
        self.assertContains(resp, 'hi there')
        worker = Worker.objects.get(user__username='alice')
        self.assertEqual(worker.gmail_address, 'alice.aardvark@gmail.com')
        self.assertEqual(worker.notes, 'hi there')

        resp = self.assertPostOK(
            'worker-update',
            data={
                'gmail_address': 'alice.aardvark@gmail.com',
                'venmo_handle': '@Alice-Aardvark-42',
                'notes': 'hello again'
            },
            follow=True)
        self.assertContains(resp, 'alice.aardvark')
        self.assertContains(resp, 'hello again')

        worker = Worker.objects.get(user__username='alice')
        self.assertEqual(worker.gmail_address, 'alice.aardvark@gmail.com')
        self.assertEqual(worker.venmo_handle, '@Alice-Aardvark-42')
        self.assertEqual(worker.notes, 'hello again')

        resp = self.assertPostOK(
            'worker-update',
            data={
                'venmo_handle': 'AARDVARK',
                'notes': 'this should fail due to validation errors'
            },
            follow=True)
        self.assertContains(resp, "Enter a valid value.")
        worker = Worker.objects.get(user__username='alice')
        self.assertEqual(worker.gmail_address, 'alice.aardvark@gmail.com')
        self.assertEqual(worker.venmo_handle, '@Alice-Aardvark-42')
        self.assertEqual(worker.notes, 'hello again')

        resp = self.assertPostOK(
            'worker-update',
            data={
                'gmail_address': 'alice.aardvark',
                'notes': 'this should fail due to validation errors'
            },
            follow=True)
        self.assertContains(resp, "Enter a valid value.")
        worker = Worker.objects.get(user__username='alice')
        self.assertEqual(worker.gmail_address, 'alice.aardvark@gmail.com')
        self.assertEqual(worker.venmo_handle, '@Alice-Aardvark-42')
        self.assertEqual(worker.notes, 'hello again')

    def test_claim_limits(self) -> None:
        alice: User = UserFactory.create(username='alice')
        self.login(alice)
        self.assertPostOK('worker-update', data={'notes': 'hi'}, follow=True)

        folder = JobFolderFactory.create(max_pending=3, max_total=5)
        jobs = JobFactory.create_batch(10, folder=folder)

        for i in range(0, 3):
            self.assertContains(
                self.assertPostOK('job-claim', jobs[i].pk, follow=True),
                "You have successfully claimed",
            )
        for i in range(0, 3):
            self.assertContains(
                self.assertPostOK('job-claim', jobs[i].pk, follow=True),
                "This task is already claimed",
            )

        self.assertContains(
            self.assertPostOK('job-claim', jobs[3].pk, follow=True),
            "maximum number of pending tasks",
        )

        for i in range(0, 3):
            Job.objects.filter(pk__in=[jobs[i].pk for i in range(3)]).update(progress="JOB_VFD")

        for i in range(3, 5):
            self.assertContains(
                self.assertPostOK('job-claim', jobs[i].pk, follow=True),
                "You have successfully claimed",
            )
        self.assertContains(
            self.assertPostOK('job-claim', jobs[5].pk, follow=True),
            "maximum number of total tasks",
        )


class InvoiceTest(EvanTestCase):

    def test_semester_invoices(self) -> None:
        semester: Semester = SemesterFactory.create(active=True)
        alice: Student = StudentFactory.create(user__username='alice', semester=semester)
        bob: Student = StudentFactory.create(user__username='bob', semester=semester)
        carol: Student = StudentFactory.create(user__username='carol', semester=semester)
        invoice_alice = InvoiceFactory.create(student=alice)
        invoice_bob = InvoiceFactory.create(student=bob)
        invoice_carol = InvoiceFactory.create(student=carol)
        del invoice_carol

        PaymentLogFactory.create(invoice=invoice_alice, amount=50)
        PaymentLogFactory.create(invoice=invoice_bob, amount=70)
        PaymentLogFactory.create(invoice=invoice_alice, amount=150)

        worker_alice = WorkerFactory.create(user=alice.user)
        worker_carol = WorkerFactory.create(user=carol.user)

        JobFactory.create(
            assignee=worker_alice,
            progress="JOB_VFD",
            payment_preference="PREF_INVCRD",
            usd_bounty=17.64,
            semester=semester,
        )
        JobFactory.create(
            assignee=worker_alice,
            progress="JOB_VFD",
            payment_preference="PREF_INVCRD",
            usd_bounty=40.96,
            semester=semester,
        )
        JobFactory.create(
            assignee=worker_alice,
            progress="JOB_VFD",
            payment_preference="PREF_PROBONO",
            usd_bounty=1000,
            semester=semester,
        )
        JobFactory.create(
            assignee=worker_alice,
            progress="JOB_REV",
            payment_preference="PREF_INVCRD",
            usd_bounty=1000,
            semester=semester,
        )
        JobFactory.create(
            assignee=worker_carol,
            assignee__user=carol.user,
            progress="JOB_VFD",
            payment_preference="PREF_INVCRD",
            usd_bounty=130,
            semester=semester,
        )
        JobFactory.create(
            assignee=worker_carol,
            assignee__user=carol.user,
            progress="JOB_VFD",
            payment_preference="PREF_INVCRD",
            usd_bounty=130,
            # but create a random other semester for it
        )

        invoices = get_semester_invoices_with_annotations(semester)
        self.assertEqual(invoices.get(student=alice).stripe_total, Decimal(200))  # type: ignore
        self.assertEqual(
            invoices.get(student=alice).job_total,  # type: ignore
            Decimal('58.60'))
        self.assertEqual(invoices.get(student=bob).stripe_total, Decimal(70))  # type: ignore
        self.assertEqual(invoices.get(student=bob).job_total, Decimal(0))  # type: ignore
        self.assertEqual(invoices.get(student=carol).stripe_total, Decimal(0))  # type: ignore
        self.assertEqual(invoices.get(student=carol).job_total, Decimal(130))  # type: ignore
