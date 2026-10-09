from fastapi.testclient import TestClient

from docucompare.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_extract_txt():
    response = client.post(
        "/documents/extract",
        files={
            "file": (
                "contract.txt",
                b"Payment is due within 30 days.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["file_name"] == "contract.txt"
    assert data["file_type"] == "txt"
    assert data["page_count"] == 1
    assert "30 days" in data["pages"][0]["text"]


def test_reject_unsupported_file():
    response = client.post(
        "/documents/extract",
        files={
            "file": (
                "image.png",
                b"fake image",
                "image/png",
            )
        },
    )

    assert response.status_code == 400


def test_reject_empty_txt():
    response = client.post(
        "/documents/extract",
        files={
            "file": (
                "empty.txt",
                b"   ",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400