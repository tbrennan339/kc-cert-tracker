import re

CERT_PATTERNS = {
        # CompTIA
        "CompTIA A+": r'comptia\s+a\+|comptia\s+a\s+plus|\ba\+\s+cert',
        "CompTIA Network+": r'network\+|comptia\s+network',
        "CompTIA Security+": r'security\+|comptia\s+security|sec\+',
        "CompTIA CySA+": r'cysa\+|comptia\s+cysa',
        "CompTIA CASP+": r'casp\+|comptia\s+casp',
        "CompTIA Linux+": r'linux\+|comptia\s+linux',
        "CompTIA Server+": r'server\+|comptia\s+server',
        "CompTIA Cloud+": r'cloud\+|comptia\s+cloud',
        "CompTIA Data+": r'data\+|comptia\s+data',
        "CompTIA PenTest+": r'pentest\+|comptia\s+pentest',

        # Cisco
        "CCNA": r'\bccna\b',
        "CCNP": r'\bccnp\b',
        "CCIE": r'\bccie\b',
        "CCST": r'\bccst\b',

        # ISC2
        "CISSP": r'\bcissp\b',
        "CCSP": r'\bccsp\b',
        "SSCP": r'\bsscp\b',

        # ISACA
        "CISM": r'\bcism\b',
        "CISA": r'\bcisa\b',
        "CRISC": r'\bcrisc\b',
        "CGEIT": r'\bcgeit\b',

        # EC-Council
        "CEH": r'\bceh\b',
        "CHFI": r'\bchfi\b',

        # Microsoft - Azure
        "AZ-900": r'\baz[-\s]?900\b',
        "AZ-104": r'\baz[-\s]?104\b',
        "AZ-204": r'\baz[-\s]?204\b',
        "AZ-305": r'\baz[-\s]?305\b',
        "AZ-400": r'\baz[-\s]?400\b',
        "AZ-500": r'\baz[-\s]?500\b',
        "AZ-700": r'\baz[-\s]?700\b',
        "AZ-800": r'\baz[-\s]?800\b',
        "AZ-801": r'\baz[-\s]?801\b',

        # Microsoft - MS exams
        "MS-102": r'\bms[-\s]?102\b',
        "MS-700": r'\bms[-\s]?700\b',
        "MS-900": r'\bms[-\s]?900\b',

        # Microsoft - MD exams
        "MD-102": r'\bmd[-\s]?102\b',

        # Microsoft - SC exams
        "SC-100": r'\bsc[-\s]?100\b',
        "SC-200": r'\bsc[-\s]?200\b',
        "SC-300": r'\bsc[-\s]?300\b',
        "SC-400": r'\bsc[-\s]?400\b',
        "SC-900": r'\bsc[-\s]?900\b',

        # Microsoft - Role-based names
        "Microsoft Certified: Azure Administrator": r'azure\s+administrator\s+associate',
        "Microsoft Certified: Azure Solutions Architect": r'azure\s+solutions\s+architect',

        # AWS
        "AWS Cloud Practitioner": r'aws\s+cloud\s+practitioner|\bclf[-\s]?c0[12]\b',
        "AWS Solutions Architect Associate": r'aws\s+solutions\s+architect\s+associate|\bsaa[-\s]?c0[23]\b',
        "AWS Solutions Architect Professional": r'aws\s+solutions\s+architect\s+professional|\bsap[-\s]?c0[12]\b',
        "AWS SysOps Administrator": r'aws\s+sysops|\bsoa[-\s]?c0[12]\b',
        "AWS Developer Associate": r'aws\s+developer\s+associate|\bdva[-\s]?c0[12]\b',
        "AWS DevOps Engineer Professional": r'aws\s+devops\s+engineer|\bdop[-\s]?c0[12]\b',
        "AWS Security Specialty": r'aws\s+security\s+specialty|\bscs[-\s]?c0[12]\b',
        "AWS Advanced Networking Specialty": r'aws\s+advanced\s+networking|\bans[-\s]?c0[12]\b',
        "AWS Database Specialty": r'aws\s+database\s+specialty|\bdbs[-\s]?c01\b',
        "AWS Machine Learning Specialty": r'aws\s+machine\s+learning\s+specialty|\bmls[-\s]?c01\b',

        # Google Cloud
        "Google Cloud Digital Leader": r'cloud\s+digital\s+leader',
        "Google Associate Cloud Engineer": r'associate\s+cloud\s+engineer',
        "Google Professional Cloud Architect": r'professional\s+cloud\s+architect',
        "Google Professional Cloud DevOps Engineer": r'professional\s+cloud\s+devops',
        "Google Professional Cloud Security Engineer": r'professional\s+cloud\s+security\s+engineer',
        "Google Professional Cloud Network Engineer": r'professional\s+cloud\s+network\s+engineer',
        "Google Professional Data Engineer": r'professional\s+data\s+engineer',

        # ITIL / PMP / TOGAF
        "ITIL": r'\bitil\b',
        "PMP": r'\bpmp\b',
        "TOGAF": r'\btogaf\b',

        # Kubernetes / Linux / Cloud Native
        "CKA": r'\bcka\b',
        "CKAD": r'\bckad\b',
        "CKS": r'\bcks\b',
        "LFCS": r'\blfcs\b',
        "RHCSA": r'\brhcsa\b',
        "RHCE": r'\brhce\b',

        # GIAC / SANS
        "GSEC": r'\bgsec\b',
        "GCIH": r'\bgcih\b',
        "GCIA": r'\bgcia\b',
        "GPEN": r'\bgpen\b',
        "GWAPT": r'\bgwapt\b',
        "GCFE": r'\bgcfe\b',
        "GNFA": r'\bgnfa\b',
        "OSCP": r'\boscp\b',
        "OSEP": r'\bosep\b',
        "OSWP": r'\boswp\b',
    }

def extract_certs(jobs: list[dict]) -> list[dict]:
    """
    Extract certification mentions from job descriptions.

    Args:
        jobs: List of job dicts from bronze layer

    Returns:
        List of cleaned job dicts with 'certs_found' field added
    """

    results = []

    for job in jobs:
        description = job.get("description") or ""
        found = []
        for cert_name, pattern in CERT_PATTERNS.items():
            if re.search(pattern, description, re.IGNORECASE):
                found.append(cert_name)

        results.append({
            "theirstack_id": job.get("id"),
            "job_title": job.get("job_title"),
            "date_posted": job.get("date_posted"),
            "source_url": job.get("source_url"),
            "company": job.get("company"),
            "location": job.get("location"),
            "remote": job.get("remote"),
            "hybrid": job.get("hybrid"),
            "reposted": job.get("reposted"),
            "min_annual_salary": job.get("min_annual_salary"),
            "max_annual_salary": job.get("max_annual_salary"),
            "description": description,
            "certs_found": found,
        })
    return results