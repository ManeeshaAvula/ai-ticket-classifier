"""Tests for the classifier wrapper around the trained pipeline."""

from app.classifier import classifier

BILLING_TEXT = "I was charged twice for my subscription this month and need a refund for the duplicate payment on my invoice."
ACCESS_TEXT = "I forgot my password and the reset email never arrives, so I am locked out of my account."
SHIPPING_TEXT = "My order was supposed to arrive last week and the tracking has not updated in five days."
TECH_TEXT = "The app crashes every time I try to upload a file and shows error code 500."
GENERAL_TEXT = "Do you have a user guide for new teams? We are evaluating tools and want to learn more."


def test_model_is_loaded():
    assert classifier.is_loaded
    assert set(classifier.labels) == {
        "billing",
        "technical_support",
        "account_access",
        "shipping",
        "general",
    }


def test_predict_billing():
    label, confidence = classifier.predict(BILLING_TEXT)
    assert label == "billing"
    assert 0.0 <= confidence <= 1.0


def test_predict_account_access():
    label, confidence = classifier.predict(ACCESS_TEXT)
    assert label == "account_access"
    assert 0.0 <= confidence <= 1.0


def test_predict_shipping():
    label, _ = classifier.predict(SHIPPING_TEXT)
    assert label == "shipping"


def test_predict_batch():
    results = classifier.predict_batch([BILLING_TEXT, TECH_TEXT, GENERAL_TEXT])
    assert [label for label, _ in results] == [
        "billing",
        "technical_support",
        "general",
    ]
    assert all(0.0 <= confidence <= 1.0 for _, confidence in results)
