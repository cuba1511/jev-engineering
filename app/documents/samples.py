"""Demo cases: a document, what we expected, and the outcome we expect Jev to lead to."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Sample:
    title: str
    expected_type: str
    holder_name: str
    document_text: str
    expected_status: str


PAYSLIP_LUCIA = """\
RECIBO INDIVIDUAL JUSTIFICATIVO DEL PAGO DE SALARIOS
Empresa: Inmobiliaria Horizonte S.L.   CIF: B-87654321
Trabajadora: Lucía Martín García   DNI: 12345678Z
Periodo de liquidación: 01/08/2026 - 31/08/2026
DEVENGOS
  Salario base ............ 2.450,00 €
  Complementos ............   350,00 €
  TOTAL DEVENGADO ......... 2.800,00 €
DEDUCCIONES
  Contingencias comunes (4,70%) .. 131,60 €
  Desempleo (1,55%) ..............  43,40 €
  IRPF (15%) ..................... 420,00 €
  TOTAL A DEDUCIR ................ 595,00 €
LÍQUIDO TOTAL A PERCIBIR ......... 2.205,00 €
Fecha de pago: 31/08/2026
"""

SAMPLES = [
    Sample(
        title="Nómina correcta",
        expected_type="payslip",
        holder_name="Lucia Martin",
        document_text=PAYSLIP_LUCIA,
        expected_status="approved",
    ),
    Sample(
        title="Nómina de otra persona",
        expected_type="payslip",
        holder_name="Carlos Pérez Ruiz",
        document_text=PAYSLIP_LUCIA,
        expected_status="rejected",
    ),
    Sample(
        title="Sube un contrato cuando pedimos la nómina",
        expected_type="payslip",
        holder_name="Lucía Martín García",
        document_text="""\
CONTRATO DE ARRENDAMIENTO DE VIVIENDA
En Madrid, a 1 de septiembre de 2026.
ARRENDADOR: Jorge Sánchez Vidal, DNI 87654321X.
ARRENDATARIA: Lucía Martín García, DNI 12345678Z.
Vivienda: Calle Alcalá 120, 3ºB, 28009 Madrid.
Renta mensual: 1.150 € pagaderos los cinco primeros días de cada mes.
Duración: un año desde la firma, prorrogable.
Firmado por ambas partes.
""",
        expected_status="rejected",
    ),
    Sample(
        title="Factura incompleta",
        expected_type="invoice",
        holder_name="Lucía Martín García",
        document_text="""\
FACTURA
Reformas Castellana
Cliente: Lucía Martín García
Concepto: Pintura del salón y cocina ........ 1.200,00 €
Concepto: Cambio de grifería ................   180,00 €
Total: ______
""",
        expected_status="rejected",
    ),
    Sample(
        title="DNI con datos contradictorios",
        expected_type="id_document",
        holder_name="Lucía Martín García",
        document_text="""\
REINO DE ESPAÑA - DOCUMENTO NACIONAL DE IDENTIDAD
Apellidos: MARTÍN GARCÍA
Nombre: LUCÍA
Nacionalidad: ESP
Fecha de nacimiento: 14 03 1991
DNI: 12345678Z
Válido hasta: 22 05 2031
IDESP<<12345678Z<<<<<<<<<<<<<<<
9103148F3105229ESP<<<<<<<<<<<6
MARTIN<GARCIA<<LUCIA<<<<<<<<<<<
Número de soporte: CAA123456 - DNI 87654321X
""",
        expected_status="rejected",
    ),
]
