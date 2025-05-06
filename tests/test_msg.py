# -*- coding: utf-8 -*-
from pprint import pprint  # noqa

from .support import TestCase


class RFC822Test(TestCase):
    def test_thunderbird(self):
        fixture_path, entity = self.fixture("testThunderbirdEml.eml")
        self.manager.ingest(fixture_path, entity)
        self.assertSuccess(entity)
        pprint(entity.to_dict())
        self.assertEqual(entity.first("subject"), "JUnit test message")
        self.assertIn("Dear Vladimir", entity.first("bodyText"))

    def test_naumann(self):
        fixture_path, entity = self.fixture("fnf.msg")
        self.manager.ingest(fixture_path, entity)
        self.assertSuccess(entity)
        self.assertIn("Innovationskongress", entity.first("subject"))
        self.assertIn("freiheit.org", entity.first("bodyHtml"))
        self.assertEqual(entity.schema.name, "Email")

    def test_mbox(self):
        fixture_path, entity = self.fixture("plan.mbox")
        self.manager.ingest(fixture_path, entity)
        self.assertSuccess(entity)
        self.assertEqual(entity.schema.name, "Package")

    def test_base64(self):
        fixture_path, entity = self.fixture("email_base64.eml")
        self.manager.ingest(fixture_path, entity)
        self.assertSuccess(entity)
        self.assertEqual(entity.schema.name, "Email")
        self.assertEqual(entity.get("bodyText"), ["Base64 email payload"])

    def test_multipart_alternative(self):
        fixture_path, entity = self.fixture("email_multipart_alternative.eml")
        self.manager.ingest(fixture_path, entity)
        self.assertSuccess(entity)
        self.assertEqual(entity.schema.name, "Email")
        self.assertEqual(
            entity.get("bodyText"), ["This is a **multipart/alternative** message."]
        )
        self.assertEqual(
            entity.get("bodyHtml"),
            ["This is a <strong>multipart/alternative</strong> message."],
        )

    def test_multipart_mixed(self):
        fixture_path, entity = self.fixture("email_multipart_mixed.eml")
        self.manager.ingest(fixture_path, entity)
        self.assertSuccess(entity)
        self.assertEqual(entity.schema.name, "Email")
        self.assertEqual(
            entity.get("bodyText"),
            [
                "This is the first part (plaintext)",
                "This is the second part (HTML)",
                "This is the third part (plaintext)",
                "This is the fourth part (HTML)",
            ],
        )
        self.assertEqual(
            entity.get("bodyHtml"),
            [
                "This is the first part (plaintext)",
                "This is the second part (HTML)",
                "This is the third part (plaintext)",
                "This is the fourth part (HTML)",
            ],
        )

    def test_multipart_nested(self):
        fixture_path, entity = self.fixture("email_multipart_nested.eml")
        self.manager.ingest(fixture_path, entity)
        self.assertSuccess(entity)
        self.assertEqual(entity.schema.name, "Email")
        self.assertEqual(
            entity.get("bodyText"),
            [
                "This is the **first** part",
                "This is the second part",
            ],
        )
        self.assertEqual(
            entity.get("bodyHtml"),
            [
                "This is the <strong>first</strong> part",
                "This is the second part",
            ],
        )

    def test_plaintext_encode_markup(self):
        fixture_path, entity = self.fixture("email_encode_markup.eml")
        self.manager.ingest(fixture_path, entity)
        self.assertSuccess(entity)
        self.assertEqual(entity.schema.name, "Email")
        self.assertEqual(
            entity.get("bodyText"),
            [
                "This is the body of a plaintext message.\n\nEven though it's plaintext, it contains some <strong>HTML markup</strong>.",
            ],
        )
        self.assertEqual(
            entity.get("bodyHtml"),
            [
                "This is the body of a plaintext message.<br><br>Even though it&#x27;s plaintext, it contains some &lt;strong&gt;HTML markup&lt;/strong&gt;.",
            ],
        )

    def test_html_strip_markup(self):
        fixture_path, entity = self.fixture("email_strip_markup.eml")
        self.manager.ingest(fixture_path, entity)
        self.assertSuccess(entity)
        self.assertEqual(entity.schema.name, "Email")
        self.assertEqual(
            entity.get("bodyText"),
            [
                "This is the body of an HTML message.",
            ],
        )
        self.assertEqual(
            entity.get("bodyHtml"),
            [
                "This is the body of an <strong>HTML</strong> message.",
            ],
        )
        self.assertNotIn(
            "This is the body of an HTML message.", entity.get("indexText")
        )

    def test_attached_email(self):
        fixture_path, entity = self.fixture("email_attached_plaintext.eml")
        self.manager.ingest(fixture_path, entity)
        self.assertSuccess(entity)
        self.assertEqual(
            entity.get("bodyText"),
            ["This is the body of the email that contains the attachment."],
        )

        fixture_path, entity = self.fixture("email_attached_alternative.eml")
        self.manager.ingest(fixture_path, entity)
        self.assertSuccess(entity)
        self.assertEqual(
            entity.get("bodyText"),
            ["This is the body of the email that contains the attachment."],
        )

    def test_attached_inline_email(self):
        fixture_path, entity = self.fixture("email_attached_inline.eml")
        self.manager.ingest(fixture_path, entity)
        self.assertSuccess(entity)
        self.assertEqual(
            entity.get("bodyText"),
            [
                "This is the body of the email that contains the attachment.",
                "From: john.doe@example.org\nTo: jane.doe@example.org\nSubject: Plaintext only",
                "This is the body of a plaintext message.",
            ],
        )
        self.assertEqual(
            entity.get("bodyHtml"),
            [
                "This is the body of the email that contains the attachment.",
                "From: john.doe@example.org<br>To: jane.doe@example.org<br>Subject: Plaintext only",
                "This is the body of a plaintext message.",
            ],
        )

    def test_headers(self):
        fixture_path, entity = self.fixture("email_multiline_headers.eml")
        self.manager.ingest(fixture_path, entity)
        self.assertSuccess(entity)
        self.assertEqual(
            entity.get("from"),
            [
                "Отдел по работе с прохождением законопроектов <redacted@example.com>",
            ],
        )
        self.assertEqual(
            entity.get("subject"),
            [
                "Дополнительное заключение Профильного Комитета на проект закона №145-Д",
            ]
        )
