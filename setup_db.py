import os
import sqlite3

from werkzeug.security import generate_password_hash


EMPLOYERS = [
    ("careers@harbourviewbank.com.au", "Harbourview Bank", "Retail banking and digital payments provider.", "Sydney"),
    ("talent@southerncrosshealth.com.au", "Southern Cross Health", "Private healthcare network with clinics across NSW and Victoria.", "Melbourne"),
    ("recruitment@metromarket.com.au", "MetroMarket Group", "National retail and ecommerce operator.", "Sydney"),
    ("jobs@northbridgeinsurance.com.au", "Northbridge Insurance", "Insurance and claims technology company.", "Brisbane"),
    ("people@pacificretail.com.au", "Pacific Retail Group", "Consumer retail group with online and store operations.", "Sydney"),
    ("careers@civiclinkservices.gov.au", "CivicLink Services", "Public sector service delivery and citizen support provider.", "Canberra"),
    ("recruitment@bluewaterenergy.com.au", "Bluewater Energy", "Renewable energy and utilities company.", "Perth"),
    ("jobs@summiteducation.edu.au", "Summit Education Services", "Education services provider supporting universities and training teams.", "Wollongong"),
    ("careers@riverstonedigital.com.au", "Riverstone Digital", "Software consultancy building web, cloud, and data platforms.", "Sydney"),
    ("talent@grantonadvisory.com.au", "Granton Advisory", "Business consulting and enterprise transformation firm.", "Melbourne"),
    ("jobs@eastgatetelco.com.au", "Eastgate Telecommunications", "Telecommunications infrastructure and customer systems provider.", "Adelaide"),
    ("careers@meridianproperty.com.au", "Meridian Property Group", "Commercial property and facilities management business.", "Sydney"),
    ("people@coastalutilities.com.au", "Coastal Utilities", "Water and infrastructure services operator.", "Brisbane"),
    ("recruitment@brightpathlearning.com.au", "BrightPath Learning", "Digital learning and workforce training company.", "Melbourne"),
    ("jobs@ironbridgelogistics.com.au", "Ironbridge Logistics", "Freight, warehousing, and supply chain company.", "Sydney"),
    ("careers@auroramedicalsystems.com.au", "Aurora Medical Systems", "Healthcare software and medical operations systems provider.", "Melbourne"),
    ("talent@stonehavenfinancial.com.au", "Stonehaven Financial", "Wealth management and financial planning firm.", "Sydney"),
    ("jobs@citylinetransport.com.au", "Cityline Transport", "Urban transport operations and scheduling provider.", "Melbourne"),
    ("careers@opaldata.com.au", "Opal Data Services", "Data engineering, reporting, and analytics services company.", "Sydney"),
    ("people@newcastlemanufacturing.com.au", "Newcastle Manufacturing", "Industrial manufacturing and operations technology company.", "Newcastle"),
]


JOB_TEMPLATES = [
    ("Software Engineer", "Build and maintain business applications used by internal teams and customers.", "Python, JavaScript, SQL, Git", "Bachelor degree in Computer Science or equivalent experience", "3-5 Years", "Full-time"),
    ("Backend Software Engineer", "Develop APIs, service integrations, and database-backed features.", "Python, Flask, SQL, REST API", "Bachelor degree in Software Engineering or related field", "3-5 Years", "Full-time"),
    ("Frontend Engineer", "Create responsive web interfaces and reusable UI components.", "JavaScript, React, HTML, CSS", "Bachelor degree or equivalent frontend experience", "3-5 Years", "Full-time"),
    ("Full Stack Developer", "Work across frontend, backend, and database features for customer-facing products.", "React, Python, Flask, SQL", "Bachelor degree or equivalent full stack experience", "3-5 Years", "Full-time"),
    ("Graduate Software Developer", "Support feature delivery, bug fixes, and code reviews while building engineering skills.", "JavaScript, Python, HTML, CSS", "Bachelor degree in Computer Science or Information Technology", "0-3 Years", "Full-time"),
    ("Junior Web Developer", "Assist with website maintenance, small feature builds, and browser testing.", "HTML, CSS, JavaScript, Git", "Diploma or Bachelor degree in IT", "0-3 Years", "Full-time"),
    ("Data Analyst", "Prepare reports, analyse operational data, and explain trends to stakeholders.", "SQL, Excel, Power BI, Data Analysis", "Bachelor degree in Data Science, Business, or related field", "3-5 Years", "Full-time"),
    ("Business Analyst", "Gather business requirements, document workflows, and support delivery teams.", "Requirements Analysis, SQL, Process Mapping, Jira", "Bachelor degree in Business Information Systems or related field", "3-5 Years", "Full-time"),
    ("Systems Analyst", "Analyse existing systems, document changes, and support implementation planning.", "Systems Analysis, SQL, Documentation, Testing", "Bachelor degree in Information Systems or equivalent experience", "3-5 Years", "Full-time"),
    ("DevOps Engineer", "Maintain CI/CD pipelines, deployment tooling, and cloud infrastructure.", "AWS, Docker, CI/CD, Linux", "Bachelor degree or equivalent infrastructure experience", "3-5 Years", "Full-time"),
    ("Cloud Infrastructure Engineer", "Support cloud environments, monitoring, and infrastructure automation.", "AWS, Azure, Terraform, Linux", "Bachelor degree in IT or equivalent cloud experience", "3-5 Years", "Full-time"),
    ("Cyber Security Analyst", "Monitor security alerts, investigate incidents, and improve security controls.", "Cyber Security, SIEM, Network Security, Incident Response", "Bachelor degree in Cyber Security or related field", "3-5 Years", "Full-time"),
    ("QA Automation Engineer", "Build automated tests and improve regression testing coverage.", "Testing, Selenium, Python, API Testing", "Bachelor degree or equivalent QA automation experience", "3-5 Years", "Full-time"),
    ("Test Analyst", "Prepare test cases, run functional testing, and document defects.", "Manual Testing, Test Planning, Jira, SQL", "Bachelor degree or equivalent testing experience", "0-3 Years", "Contract"),
    ("UX/UI Designer", "Design user flows, wireframes, prototypes, and production-ready interface assets.", "Figma, UI/UX, Prototyping, User Research", "Bachelor degree in Design or equivalent portfolio experience", "3-5 Years", "Full-time"),
    ("Product Designer", "Improve product usability through research, prototyping, and design system work.", "Figma, Design Systems, User Research, Accessibility", "Bachelor degree in Design or equivalent experience", "3-5 Years", "Full-time"),
    ("Product Manager", "Prioritise product features, write user stories, and coordinate release planning.", "Product Management, Roadmapping, Agile, Stakeholder Management", "Bachelor degree or equivalent product experience", "5-7 Years", "Full-time"),
    ("Project Manager", "Plan delivery schedules, manage risks, and coordinate cross-functional project teams.", "Project Management, Risk Management, Agile, Reporting", "Bachelor degree or project management certification", "5-7 Years", "Full-time"),
    ("Scrum Master", "Facilitate agile ceremonies and remove delivery blockers for engineering teams.", "Agile, Scrum, Jira, Facilitation", "Scrum certification or equivalent delivery experience", "3-5 Years", "Contract"),
    ("IT Support Analyst", "Provide desktop, application, and account support to staff.", "Windows, Microsoft 365, Service Desk, Troubleshooting", "Diploma or Bachelor degree in IT", "0-3 Years", "Full-time"),
    ("Service Desk Analyst", "Handle first-level support tickets and escalate technical issues.", "Service Desk, ITIL, Microsoft 365, Customer Support", "Diploma or equivalent IT support experience", "0-3 Years", "Full-time"),
    ("Database Administrator", "Maintain database performance, backups, access controls, and data integrity.", "SQL, PostgreSQL, SQLite, Database Management", "Bachelor degree in IT or equivalent database experience", "3-5 Years", "Full-time"),
    ("Data Engineer", "Build data pipelines, transform datasets, and support analytics platforms.", "Python, SQL, ETL, Data Warehousing", "Bachelor degree in Data Engineering or related field", "3-5 Years", "Full-time"),
    ("Business Intelligence Developer", "Develop dashboards, data models, and reporting solutions.", "Power BI, SQL, Data Modelling, DAX", "Bachelor degree in Analytics, IT, or related field", "3-5 Years", "Full-time"),
    ("Machine Learning Engineer", "Develop and deploy predictive models for operational decision-making.", "Python, Machine Learning, SQL, Model Deployment", "Master degree or equivalent machine learning experience", "5-7 Years", "Full-time"),
    ("Data Scientist", "Build statistical models and communicate insights to business stakeholders.", "Python, Statistics, Machine Learning, SQL", "Master degree in Data Science, Statistics, or related field", "3-5 Years", "Full-time"),
    ("Network Engineer", "Maintain switching, routing, firewall, and network monitoring systems.", "Networking, Cisco, Firewall, Troubleshooting", "Bachelor degree or networking certification", "3-5 Years", "Full-time"),
    ("Solutions Architect", "Design solution options, technical roadmaps, and integration patterns.", "Solution Architecture, APIs, Cloud, Stakeholder Management", "Bachelor degree in IT or equivalent architecture experience", "7-9 Years", "Full-time"),
    ("Platform Engineer", "Improve developer platforms, deployment standards, and system reliability.", "Kubernetes, Docker, CI/CD, Observability", "Bachelor degree or equivalent platform engineering experience", "5-7 Years", "Full-time"),
    ("Site Reliability Engineer", "Improve reliability, monitoring, and incident response for production systems.", "Linux, Observability, Scripting, Incident Response", "Bachelor degree or equivalent SRE experience", "5-7 Years", "Full-time"),
    ("Mobile App Developer", "Develop mobile application features and maintain release quality.", "Swift, Kotlin, REST API, Mobile Testing", "Bachelor degree or equivalent mobile development experience", "3-5 Years", "Full-time"),
    ("Application Support Analyst", "Investigate application issues, run data checks, and support business users.", "SQL, Application Support, Troubleshooting, Documentation", "Diploma or Bachelor degree in IT", "0-3 Years", "Full-time"),
    ("Implementation Consultant", "Configure software solutions and support customer onboarding projects.", "Configuration, SQL, Customer Workshops, Documentation", "Bachelor degree or equivalent implementation experience", "3-5 Years", "Full-time"),
    ("Integration Developer", "Build integrations between business systems, APIs, and data services.", "REST API, Python, SQL, Integration Testing", "Bachelor degree in Software Engineering or related field", "3-5 Years", "Full-time"),
    ("Technical Writer", "Prepare API documentation, user guides, and internal process material.", "Technical Writing, API Documentation, Markdown, Research", "Bachelor degree in Communications, IT, or related field", "3-5 Years", "Contract"),
    ("Digital Project Coordinator", "Coordinate project tasks, meeting actions, and delivery reporting.", "Project Coordination, Jira, Reporting, Communication", "Bachelor degree or equivalent coordination experience", "0-3 Years", "Full-time"),
    ("Security Engineer", "Implement security tooling, hardening tasks, and vulnerability remediation.", "Cyber Security, Cloud Security, Scripting, Vulnerability Management", "Bachelor degree in Cyber Security or related field", "5-7 Years", "Full-time"),
    ("Reporting Analyst", "Maintain operational reports and help teams interpret performance metrics.", "SQL, Excel, Power BI, Reporting", "Bachelor degree in Business, Analytics, or related field", "0-3 Years", "Full-time"),
    ("CRM Administrator", "Configure CRM workflows, fields, reports, and user access.", "CRM, Data Quality, Reporting, User Support", "Bachelor degree or equivalent systems administration experience", "3-5 Years", "Full-time"),
    ("ERP Systems Analyst", "Support ERP configuration, process improvements, and system testing.", "ERP, SQL, Business Analysis, Testing", "Bachelor degree in Information Systems or related field", "3-5 Years", "Full-time"),
]


TEAMS = [
    "Customer Portal", "Payments Platform", "Claims Systems", "Online Services",
    "Data and Reporting", "Workforce Systems", "Mobile Applications",
    "Cloud Operations", "Security Operations", "Retail Technology",
    "Patient Services", "Learning Platforms", "Finance Systems",
    "Supply Chain Systems", "Digital Experience", "Infrastructure Services",
    "Enterprise Applications", "Contact Centre Technology", "Analytics Team",
    "Service Delivery"
]


LOCATIONS = [
    "Sydney", "Melbourne", "Brisbane", "Canberra", "Perth", "Adelaide",
    "Wollongong", "Newcastle", "Parramatta", "Remote"
]


WORK_MODES = ["Hybrid", "Remote", "On-site"]


SALARY_BY_EXPERIENCE = {
    "0-3 Years": ["$65k - $80k", "$70k - $85k", "$75k - $90k"],
    "3-5 Years": ["$90k - $110k", "$100k - $125k", "$110k - $135k"],
    "5-7 Years": ["$125k - $150k", "$135k - $160k", "$145k - $170k"],
    "7-9 Years": ["$155k - $180k", "$165k - $190k", "$175k - $205k"],
}


def build_employers(password_hash):
    return [
        (
            index,
            email,
            password_hash,
            company_name,
            company_info,
            email,
            location,
            1 if index == 1 else 0,
        )
        for index, (email, company_name, company_info, location)
        in enumerate(EMPLOYERS, start=1)
    ]


def build_jobs(count=200):
    jobs = []

    for index in range(count):
        title, description, skills, education, experience, job_type = JOB_TEMPLATES[index % len(JOB_TEMPLATES)]
        employer_id = (index % len(EMPLOYERS)) + 1
        company_name = EMPLOYERS[employer_id - 1][1]
        team = TEAMS[(index * 3) % len(TEAMS)]
        location = LOCATIONS[(index * 7) % len(LOCATIONS)]
        work_mode = WORK_MODES[index % len(WORK_MODES)]
        salary_options = SALARY_BY_EXPERIENCE.get(experience, SALARY_BY_EXPERIENCE["3-5 Years"])
        salary = salary_options[index % len(salary_options)]
        title_with_team = f"{title} - {team}"
        description_with_context = (
            f"{description} The role sits in the {team} team at {company_name} "
            "and works closely with business stakeholders, product teams, and technical delivery teams."
        )

        jobs.append((
            employer_id,
            title_with_team,
            company_name,
            description_with_context,
            education,
            skills,
            experience,
            work_mode,
            location,
            salary,
            job_type,
        ))

    return jobs


def setup_database():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'database', 'platform.db')
    schema_path = os.path.join(current_dir, 'database', 'schema.sql')
    db_dir = os.path.dirname(db_path)

    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())

    cursor = conn.cursor()
    password_hash = generate_password_hash('password123')

    cursor.executemany(
        """
        INSERT INTO Employers (
            id, email, password, company_name, company_info,
            contact_info, location, membership_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        build_employers(password_hash),
    )

    cursor.executemany(
        """
        INSERT INTO Jobs (
            employer_id, title, company_info, description,
            required_education, required_skills, years_experience,
            work_mode, location, salary_range, job_type
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        build_jobs(200),
    )

    candidates = [
        ('alice@uow.edu.au', password_hash, 'Alice Chen', 'alice@uow.edu.au', 'Bachelor', 'Computer Science', '3-5 Years', 'Backend developer interested in API and data projects.', '3 years Flask API work', 'Python, SQL, Flask', 'Remote', 'Wollongong', 'Wollongong', 1),
        ('bob@uow.edu.au', password_hash, 'Bob Smith', 'bob@uow.edu.au', 'Bachelor', 'Software Engineering', '0-3 Years', 'Junior web developer.', '1 year web development', 'Java, HTML, CSS', 'On-site', 'Sydney', 'Sydney', 0),
        ('charlie@uow.edu.au', password_hash, 'Charlie Davis', 'charlie@uow.edu.au', 'Master', 'Artificial Intelligence', '5-7 Years', 'Machine learning engineer.', '5 years model development', 'Python, Machine Learning, PyTorch', 'Hybrid', 'Melbourne', 'Melbourne', 1),
        ('david@uow.edu.au', password_hash, 'David Wilson', 'david@uow.edu.au', 'Bachelor', 'Information Technology', '0-3 Years', 'Frontend engineer.', '2 years JavaScript and React', 'JavaScript, React', 'Remote', 'Sydney', 'Sydney', 0),
        ('eve@uow.edu.au', password_hash, 'Eve Brown', 'eve@uow.edu.au', 'Bachelor', 'Data Science', '3-5 Years', 'Database analyst.', '4 years database management', 'SQL, Database Management', 'On-site', 'Brisbane', 'Brisbane', 0),
        ('frank@uow.edu.au', password_hash, 'Frank Miller', 'frank@uow.edu.au', 'Bachelor', 'Computer Science', '0-3 Years', 'Junior programmer.', 'Junior development projects', 'Python, C++', 'Hybrid', 'Wollongong', 'Wollongong', 0),
        ('grace@uow.edu.au', password_hash, 'Grace Lee', 'grace@uow.edu.au', 'Bachelor', 'Cloud Computing', '7-9 Years', 'Cloud and DevOps specialist.', 'Senior cloud automation', 'AWS, Cloud, DevOps', 'Remote', 'Sydney', 'Sydney', 1),
        ('hank@uow.edu.au', password_hash, 'Hank Moore', 'hank@uow.edu.au', 'Bachelor', 'Software Engineering', '0-3 Years', 'QA engineer.', '2 years QA automation', 'Testing, QA, Selenium', 'Hybrid', 'Melbourne', 'Melbourne', 0),
        ('ivy@uow.edu.au', password_hash, 'Ivy Taylor', 'ivy@uow.edu.au', 'Bachelor', 'Design', '3-5 Years', 'UI/UX designer.', '3 years product design', 'UI/UX, Figma, Design', 'On-site', 'Sydney', 'Sydney', 0),
        ('jack@uow.edu.au', password_hash, 'Jack Anderson', 'jack@uow.edu.au', 'Master', 'Software Architecture', '5-7 Years', 'Software architect.', '6 years architecture', 'Software Architecture', 'Remote', 'Wollongong', 'Wollongong', 1)
    ]

    cursor.executemany(
        """
        INSERT INTO Candidates (
            email, password, full_name, contact_info, education, major,
            years_experience, summary, work_experience, skills,
            preferred_mode, preferred_location, location, membership_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        candidates,
    )

    conn.commit()
    conn.close()
    print("Database reset successfully.")
    print("Seeded: 20 Employers, 200 Jobs, 10 Candidates.")
    print("Demo account: careers@harbourviewbank.com.au is a VIP employer with posted jobs.")


if __name__ == "__main__":
    setup_database()
