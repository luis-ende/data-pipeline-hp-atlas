-- HPA Version 21.1

SELECT 'loading data from proteinatlas.tsv' AS progress;

COPY proteinatlas
FROM '/opt/human-protein-atlas-data/proteinatlas.tsv'
DELIMITER E'\t'
ENCODING 'utf-8'
CSV HEADER;

SELECT 'proteinatlas' AS imported;

SELECT 'loading data from normal_tissue.tsv' AS progress;

COPY normal_tissue
FROM '/opt/human-protein-atlas-data/normal_tissue.tsv'
DELIMITER E'\t'
ENCODING 'utf-8'
CSV HEADER;

SELECT 'normal_tissue' AS imported;

SELECT 'loading data from pathology.tsv.' AS progress;

COPY pathology
FROM '/opt/human-protein-atlas-data/pathology.tsv'
DELIMITER E'\t'
ENCODING 'utf-8'
CSV HEADER;

SELECT 'pathology' AS imported;

SELECT 'loading data from subcellular_location.tsv.' AS progress;

COPY subcellular_location
FROM '/opt/human-protein-atlas-data/subcellular_location.tsv'
DELIMITER E'\t'
ENCODING 'utf-8'
CSV HEADER;

SELECT 'subcellular_location' AS imported;

SELECT 'loading data from rna_tissue_consensus.tsv.' AS progress;

COPY rna_tissue_consensus
FROM '/opt/human-protein-atlas-data/rna_tissue_consensus.tsv'
DELIMITER E'\t'
ENCODING 'utf-8'
CSV HEADER;

SELECT 'rna_tissue_consensus' AS imported;

SELECT 'loading data from rna_tissue_hpa.tsv.' AS progress;

COPY rna_tissue_hpa
FROM '/opt/human-protein-atlas-data/rna_tissue_hpa.tsv'
DELIMITER E'\t'
ENCODING 'utf-8'
CSV HEADER;

SELECT 'rna_tissue_hpa' AS imported;

SELECT 'loading data from rna_tissue_gtex.tsv.' AS progress;

COPY rna_tissue_gtex
FROM '/opt/human-protein-atlas-data/rna_tissue_gtex.tsv'
DELIMITER E'\t'
ENCODING 'utf-8'
CSV HEADER;

SELECT 'rna_tissue_gtex' AS imported;

SELECT 'loading data from rna_tissue_fantom.tsv.' AS progress;

COPY rna_tissue_fantom
FROM '/opt/human-protein-atlas-data/rna_tissue_fantom.tsv'
DELIMITER E'\t'
ENCODING 'utf-8'
CSV HEADER;

SELECT 'rna_tissue_fantom' AS imported;

SELECT 'loading data from rna_single_cell_type.tsv.' AS progress;

COPY rna_single_cell_type
FROM '/opt/human-protein-atlas-data/rna_single_cell_type.tsv'
DELIMITER E'\t'
ENCODING 'utf-8'
CSV HEADER;

SELECT 'rna_single_cell_type' AS imported;

SELECT 'loading data from rna_single_cell_type_tissue.tsv.' AS progress;

COPY rna_single_cell_type_tissue
FROM '/opt/human-protein-atlas-data/rna_single_cell_type_tissue.tsv'
DELIMITER E'\t'
ENCODING 'utf-8'
CSV HEADER;

SELECT 'rna_single_cell_type_tissue' AS imported;

SELECT 'loading data from rna_single_cell_read_count.tsv.' AS progress;

COPY rna_single_cell_read_count
FROM '/opt/human-protein-atlas-data/rna_single_cell_read_count.tsv'
DELIMITER E'\t'
ENCODING 'utf-8'
CSV HEADER;

SELECT 'rna_single_cell_read_count' AS imported;

SELECT 'loading data from rna_brain_gtex.tsv.' AS progress;

COPY rna_brain_gtex
FROM '/opt/human-protein-atlas-data/rna_brain_gtex.tsv'
DELIMITER E'\t'
ENCODING 'utf-8'
CSV HEADER;

SELECT 'rna_brain_gtex' AS imported;

SELECT 'loading data from rna_brain_fantom.tsv.' AS progress;

COPY rna_brain_gtex
FROM '/opt/human-protein-atlas-data/rna_brain_fantom.tsv'
DELIMITER E'\t'
ENCODING 'utf-8'
CSV HEADER;

SELECT 'rna_brain_fantom' AS imported;
