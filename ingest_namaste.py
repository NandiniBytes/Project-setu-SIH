import json
import re
from pathlib import Path

import pandas as pd
from fhir.resources.R4.codesystem import CodeSystem, CodeSystemConcept


def _read_single_excel(file_path: Path) -> pd.DataFrame:
	"""Read a single Excel file and return a DataFrame."""
	df = pd.read_excel(file_path, dtype=str)
	return df


def load_terms_from_excels(paths: list[Path]) -> pd.DataFrame:
	"""Load and combine terms from multiple Excel files; clean and normalize columns."""
	frames: list[pd.DataFrame] = []
	for p in paths:
		if not p.exists():
			raise FileNotFoundError(f"Input file not found: {p}")
		frames.append(_read_single_excel(p))

	if not frames:
		raise ValueError("No input data frames were read from Excel files.")

	combined = pd.concat(frames, ignore_index=True)

	# Normalize column names to lower case for alias matching
	lower_map = {c: str(c).strip().lower() for c in combined.columns}
	inv_map = {v: k for k, v in lower_map.items()}

	# Define aliases for required fields (case-insensitive keys)
	aliases = {
		"code": [
			"code",
			"codes",
			"ayushcode",
			"termcode",
			"icdcode",
			"namc_code",
			"numc_code",
		],
		"display": [
			"display",
			"term",
			"name",
			"label",
			"title",
			"namc_term",
			"namc_term_diacritical",
			"numc_term",
		],
		"definition": [
			"definition",
			"description",
			"def",
			"meaning",
			"notes",
			"short_definition",
			"long_definition",
		],
	}

	# Build unified columns by coalescing the first non-empty among available aliases
	for target, opts in aliases.items():
		existing_cols = [inv_map[o] for o in opts if o in inv_map]
		if not existing_cols:
			raise ValueError(
				f"Missing required column mapped to '{target}'. Available columns: {list(combined.columns)}"
			)
		tmp = combined[existing_cols].copy()
		for c in existing_cols:
			tmp[c] = (
				tmp[c]
				.astype(str)
				.str.replace("\u00A0", " ", regex=False)
				.str.replace(r"\s+", " ", regex=True)
				.str.strip()
			)
		# Coalesce left-to-right
		coalesced = tmp.replace("", pd.NA).bfill(axis=1).iloc[:, 0].fillna("")
		combined[target] = coalesced

	# Ensure required columns exist
	for col in ["code", "display", "definition"]:
		if col not in combined.columns:
			raise ValueError(f"Missing required column: {col}")

	# Clean and normalize
	combined = combined.astype({"code": str, "display": str, "definition": str})
	combined = combined.fillna("")

	def _normalize(series: pd.Series) -> pd.Series:
		return (
			series.astype(str)
			.str.replace("\u00A0", " ", regex=False)
			.str.replace(r"\s+", " ", regex=True)
			.str.strip()
		)

	combined["code"] = _normalize(combined["code"])
	combined["display"] = _normalize(combined["display"])
	combined["definition"] = _normalize(combined["definition"])

	# Drop rows without a code
	combined = combined[combined["code"] != ""].reset_index(drop=True)

	return combined


def build_codesystem(terms: pd.DataFrame) -> CodeSystem:
	"""Construct a FHIR R4 CodeSystem resource from the provided terms."""
	concepts = []
	for _, row in terms.iterrows():
		concepts.append(
			CodeSystemConcept(
				code=row["code"],
				display=row["display"] or None,
				definition=row["definition"] or None,
			)
		)

	cs = CodeSystem(
		id="namaste-terminology",
		url="http://ayush.gov.in/fhir/CodeSystem/NAMASTE",
		version="1.0.0",
		name="NAMASTETerminology",
		title="NAMASTE - National AYUSH Morbidity & Standardized Terminologies Electronic",
		status="active",
		publisher="Ministry of Ayush, Government of India",
		content="complete",
		concept=concepts,
	)
	return cs


def main() -> None:
	input_paths = [
		Path("Ayurveda.xls"),
		Path("Siddha.xls"),
		Path("Unani.xls"),
	]
	output_path = Path("CodeSystem-NAMASTE.json")

	terms = load_terms_from_excels(input_paths)
	codesystem = build_codesystem(terms)

	with output_path.open("w", encoding="utf-8") as f:
		json.dump(codesystem.dict(by_alias=True), f, ensure_ascii=False, indent=2)

	print(
		f"Successfully generated {output_path.name} with {len(codesystem.concept or [])} concepts."
	)


if __name__ == "__main__":
	main()


