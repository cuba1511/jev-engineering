"""Verification questions built with TypeSafe advanced structure.

See https://docs.typesafe.ai/primitives/advanced: instructions and criteria are JSON objects
with labeled keys (`question`, `focus`, `what`, `not_for`, `examples`, `field`) instead of strings.
"""

from typesafe_sdk import Choice, Noul


DOCUMENT_TYPES = {
    "payslip": {
        "what": "A payslip (nómina) issued by an employer to an employee for a pay period",
        "not_for": "Invoices between companies or bank statements",
        "examples": ["Nómina de marzo", "Recibo de salarios", "Devengos, deducciones y líquido a percibir"],
    },
    "id_document": {
        "what": "A national identity document or passport",
        "not_for": "Any document that only mentions an ID number, like a contract or an invoice",
        "examples": ["DNI", "NIE", "Pasaporte"],
    },
    "rental_contract": {
        "what": "A residential rental agreement between a landlord and a tenant",
        "not_for": "Purchase agreements (arras, compraventa) or rent receipts",
        "examples": ["Contrato de arrendamiento de vivienda", "Arrendador y arrendatario"],
    },
    "invoice": {
        "what": "An invoice issued by a seller to a customer for goods or services",
        "not_for": "Payslips, quotes (presupuestos) or receipts without tax details",
        "examples": ["Factura nº 2026-0142", "Base imponible, IVA y total"],
    },
    "other": {
        "what": "Any other kind of document, or text that is not a document",
        "examples": ["Bank statement", "Email", "Quote", "Blank or unreadable text"],
    },
}

# Required fields per document type, in the `field` shape from the advanced structure docs.
REQUIRED_FIELDS = {
    "payslip": [
        {"name": "employer", "description": "Employer company name and tax ID (CIF)"},
        {"name": "employee", "description": "Employee full name"},
        {"name": "pay_period", "description": "The month or date range the payslip covers"},
        {"name": "gross_salary", "description": "Total gross earnings (total devengado)"},
        {"name": "deductions", "description": "Withholdings such as IRPF and social security"},
        {"name": "net_salary", "description": "Net amount paid (líquido a percibir)"},
    ],
    "id_document": [
        {"name": "full_name", "description": "Holder's full name"},
        {"name": "document_number", "description": "DNI, NIE or passport number"},
        {"name": "date_of_birth", "description": "Holder's date of birth"},
        {"name": "expiry_date", "description": "Date until which the document is valid"},
    ],
    "rental_contract": [
        {"name": "parties", "description": "Names of the landlord (arrendador) and the tenant (arrendatario)"},
        {"name": "property_address", "description": "Address of the rented property"},
        {"name": "monthly_rent", "description": "Monthly rent amount"},
        {"name": "duration", "description": "Start date and duration of the contract"},
        {"name": "signatures", "description": "Signatures of both parties, or a statement that both signed"},
    ],
    "invoice": [
        {"name": "invoice_number", "description": "The identifier of the invoice"},
        {"name": "issue_date", "description": "The date the invoice was issued"},
        {"name": "issuer_tax_id", "description": "Issuer name and tax ID (NIF/CIF)"},
        {"name": "customer", "description": "Name of the invoiced customer"},
        {"name": "line_items", "description": "Itemized concepts being charged"},
        {"name": "tax", "description": "Tax breakdown, such as IVA"},
        {"name": "total", "description": "Total amount due"},
    ],
    "other": [],
}


def build_questions(expected_type: str) -> dict:
    questions = {
        "document_type": Choice(
            instructions={
                "question": "Which kind of document is `document`?",
                "focus": "Classify by what the document is, not by the documents it mentions.",
            },
            criteria=DOCUMENT_TYPES,
        ),
        "belongs_to_holder": Noul(
            instructions={
                "question": "Is `document` issued to, or does it identify, `expected.holder_name` as its holder?",
                "compare": ["expected.holder_name", "document"],
                "focus": "The holder is the employee, ID holder, tenant or invoiced customer, not the company that issues it.",
            },
            criteria={
                "true": {
                    "what": "The holder in the document is the same person as `expected.holder_name`",
                    "examples": ["Accents or capitalization differ", "The second surname is missing"],
                },
                "false": {
                    "what": "The holder is a different person, or no holder can be identified",
                    "examples": ["A different first name", "Only the issuing company is named"],
                },
            },
        ),
        "has_contradictions": Noul(
            instructions={
                "question": "Does `document` contradict itself?",
                "focus": "Look for the same fact appearing with different values in different places.",
            },
            criteria={
                "true": {
                    "what": "The same person, ID number, date or amount appears with different values",
                    "examples": ["Two different DNI numbers for the same person", "A period of March with a payment date in January of the previous year"],
                },
                "false": {
                    "what": "Every repeated fact is consistent across the document",
                },
            },
        ),
    }
    for field in REQUIRED_FIELDS[expected_type]:
        questions[f"field_{field['name']}"] = Noul(
            instructions={
                "field": field,
                "document_type": expected_type,
                "question": "Does `document` contain a value for `field`?",
            },
            criteria={
                "true": "The value is present and legible in the document",
                "false": "The value is missing, blank, or only a placeholder like XXX or ___",
            },
        )
    return questions
