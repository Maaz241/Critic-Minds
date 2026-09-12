"""
sample_demo.py
Pre-loaded demonstration dataset for Critic Minds hackathon presentation.
Subject: Biology | Grade: 8 | Topic: Photosynthesis
Includes textbook excerpt text across multiple pages with empirical data,
pre-configured sample challenges, and representative student responses.
"""
from app.ingestion.unified import UnifiedDocument, DocumentChunk

SAMPLE_FILENAME = "Biology_Grade8_Photosynthesis_Chapter4.pdf"

SAMPLE_TEXT_PAGES = [
    (
        42,
        """Chapter 4: Plant Metabolism and Energy
Section 4.1: The Fundamentals of Photosynthesis

Photosynthesis is the fundamental biochemical process by which autotrophic organisms convert solar light energy into stored chemical energy in the form of glucose. The overall chemical equation is:
6CO2 + 6H2O + Light Energy -> C6H12O6 + 6O2

This transformation takes place predominantly within the chloroplasts of palisade mesophyll cells in leaves. Chloroplasts contain chlorophyll a and chlorophyll b pigments embedded in the thylakoid membranes. These pigments absorb electromagnetic radiation primarily in the blue (430-450 nm) and red (640-660 nm) spectral regions, while reflecting green light (500-550 nm), giving leaves their characteristic green color.

Key environmental factors directly govern the rate of photosynthesis: light intensity, ambient carbon dioxide concentration, temperature, and water availability. If any one of these essential factors is at a sub-optimal level, it acts as a 'limiting factor', constraining the overall rate regardless of increases in the other variables."""
    ),
    (
        43,
        """Section 4.2: Investigating Limiting Factors — Experimental Findings

In 1905, British plant physiologist F.F. Blackman formulated the Principle of Limiting Factors. Under controlled greenhouse conditions, middle school investigators monitored the rate of photosynthesis in Elodea canadensis (waterweed) by measuring the rate of oxygen bubble production per minute across varying distances from a 100W incandescent light source.

Experimental Observation Data:
- Trial Group A (Light Intensity):
  * At 10 cm distance (High Light, 25°C, 0.04% CO2): 48 bubbles/min.
  * At 30 cm distance (Medium Light, 25°C, 0.04% CO2): 24 bubbles/min.
  * At 60 cm distance (Low Light, 25°C, 0.04% CO2): 7 bubbles/min.

- Trial Group B (CO2 Enrichment at High Light 10 cm distance, 25°C):
  * At baseline atmospheric CO2 (0.04%): 48 bubbles/min.
  * At elevated CO2 (0.10% NaHCO3 added): 82 bubbles/min.
  * At hyper-elevated CO2 (0.20% NaHCO3 added): 84 bubbles/min. Notice that beyond 0.10%, the rate plateaus, suggesting that another factor (such as enzyme saturation or light saturation) has become limiting."""
    ),
    (
        44,
        """Section 4.3: Temperature Extremes and Stomatal Regulation

Photosynthetic reactions involve critical enzymes, including Ribulose-1,5-bisphosphate carboxylase-oxygenase (RuBisCO). Enzymes have an optimal temperature range, typically between 20°C and 30°C for temperate C3 plants.

When ambient temperatures exceed 38°C to 40°C:
1. Enzyme denaturing begins, causing active sites on RuBisCO to lose their functional tertiary conformation, sharply decreasing photosynthetic yield.
2. High transpiration rates trigger guard cells to lose turgor pressure, closing the stomata to prevent catastrophic desiccation. While stomatal closure conserves moisture, it severely limits CO2 diffusion into the leaf interior, dropping internal CO2 concentration and halving net glucose synthesis even under intense midday sunlight.

Agricultural implications: Commercial greenhouse growers must carefully balance artificial lighting, heating/cooling ventilation, and supplemental CO2 injection to avoid spending energy when a different limiting factor restricts crop growth."""
    )
]


def load_demo_document() -> UnifiedDocument:
    """Creates a UnifiedDocument instance from the Grade 8 Biology dataset."""
    chunks = []
    chunk_idx = 0
    total_len = 0

    for page_num, text in SAMPLE_TEXT_PAGES:
        total_len += len(text)
        chunks.append(
            DocumentChunk(
                chunk_id=f"demo-bio-c{chunk_idx}",
                document_id="demo_biology_ch4",
                filename=SAMPLE_FILENAME,
                file_type="pdf",
                page_or_slide=f"Page {page_num}",
                section=f"Photosynthesis (Page {page_num})",
                chunk_index=chunk_idx,
                text=text.strip(),
            )
        )
        chunk_idx += 1

    return UnifiedDocument(
        document_id="demo_biology_ch4",
        filename=SAMPLE_FILENAME,
        file_type="pdf",
        chunks=chunks,
        raw_text_length=total_len,
    )


# Sample Student Submissions for Quick Testing & Demonstration
SAMPLE_STRONG_RESPONSE = (
    "Based on the experimental data from Page 43, the greenhouse operator should prioritize adding "
    "supplemental carbon dioxide rather than increasing the light fixtures. At 10 cm (high light), "
    "elevating CO2 from 0.04% to 0.10% nearly doubled the rate from 48 to 82 bubbles per minute. "
    "However, they must also ensure the temperature stays below 35°C because Page 44 notes that extreme "
    "temperatures cause stomata to close, which cuts off internal CO2 and denatures RuBisCO enzymes. "
    "An alternative argument is that more powerful LED lighting could boost photosynthesis, but the data "
    "shows that beyond 0.10% CO2, light was already sufficient and a plateau occurred, meaning light was no "
    "longer the primary limiting factor. Therefore, moderate CO2 enrichment coupled with climate ventilation "
    "is the most cost-effective and biologically justified solution."
)

SAMPLE_WEAK_RESPONSE = (
    "Plants need light and water to grow big. I think they should just turn on more lights because light "
    "makes photosynthesis happen faster. If they put 5 lights it will make lots of oxygen and glucose."
)
