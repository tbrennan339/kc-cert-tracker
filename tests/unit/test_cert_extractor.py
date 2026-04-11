from src.etl.transformers.cert_extractor import extract_certs

def make_job(description):
    '''Helper to create a minimal job dict for testing.'''
    return {
        "job_title": "Test Job",
        "date_posted": "2026-01-01",
        "source_url": "",
        "company": "Test Co",
        "location": "Kansas City, MO",
        "remote": False,
        "hybrid": False,
        "reposted": False,
        "min_annual_salary": None,
        "max_annual_salary": None,
        "description": description,
    }

def test_extracts_security_plus():
    result = extract_certs([make_job("Must have Security+ certificate")])
    assert "CompTIA Security+" in result[0]["certs_found"]

def test_extracts_security_plus_shorthand():
    result = extract_certs([make_job("Candidates with Sec+ certificate preferred")])
    assert "CompTIA Security+" in result[0]["certs_found"]

def test_multiple_mentions_of_same_cert():
    result = extract_certs([make_job("Candidates with Sec+ aka CompTIA Security+ certificate preferred")])
    assert len(result[0]["certs_found"]) == 1

def test_extracts_multiple_certs():
    result = extract_certs([make_job("Bonus is candidate has A+ Certification, Net+, or Sec+")])
    assert "CompTIA A+" in result[0]["certs_found"]
    assert "CompTIA Network+" in result[0]["certs_found"]
    assert "CompTIA Security+" in result[0]["certs_found"]

def test_extracts_aws_cert():
    result = extract_certs([make_job("AWS Cloud Practitioner required")])
    assert "AWS Cloud Practitioner" in result[0]["certs_found"]

def test_extracts_azure_exam_number():
    result = extract_certs([make_job("AZ-900 or AZ-104 certification preferred")])
    assert "AZ-900" in result[0]["certs_found"]
    assert "AZ-104" in result[0]["certs_found"]

def test_no_certs_found():
    result = extract_certs([make_job("Looking for a Python developer with 5 years experience")])
    assert result[0]["certs_found"] == []

def test_handles_empty_description():
    result = extract_certs([make_job(None)])
    assert result[0]["certs_found"] == []

def test_case_insensitive():
    result = extract_certs([make_job("Must have CCNA or ccna certification")])
    assert "CCNA" in result[0]["certs_found"]
    assert len(result[0]["certs_found"]) == 1