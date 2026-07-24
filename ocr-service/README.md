# AI Medical Copilot — OCR Pipeline Service

A FastAPI microservice providing document preprocessing, Tesseract OCR extraction, and regex heuristic field parsing for medical prescription images.

---

## 1. Setup & Execution Instructions

### Prerequisites
- Python 3.9+
- Tesseract OCR system binary installed:
  - **Windows**: Install via `winget install UB-Mannheim.TesseractOCR` or download installer from UB-Mannheim. Ensure `tesseract` is added to System PATH.
  - **Linux**: `sudo apt-get install tesseract-ocr`
  - **macOS**: `brew install tesseract`

### Step 1: Install Python Dependencies
```bash
cd ocr-service
pip install -r requirements.txt
```

### Step 2: Launch FastAPI Server
```bash
python main.py
```
Or using uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The interactive OpenAPI documentation will be available at:
`http://localhost:8000/docs`

---

## 2. Frontend Integration (`fetch` snippet)

Here is the exact `fetch()` implementation used by the EMR dashboard (`script.js`) to call the `/ocr/extract` endpoint:

```javascript
async function scanPrescriptionImage(fileObject) {
  const formData = new FormData();
  formData.append('file', fileObject);

  try {
    const response = await fetch('http://localhost:8000/ocr/extract', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`OCR service HTTP error: ${response.status}`);
    }

    const data = await response.json();
    
    // Map returned JSON fields onto existing EMR form DOM IDs
    document.getElementById('complaint-input').value = data.complaint || (data.complaints ? data.complaints.join(', ') : '');
    document.getElementById('diagnosis-input').value = data.diagnosis || '';
    document.getElementById('investigation-input').value = data.investigation || '';
    document.getElementById('remarks-input').value = data.notes || '';

    // Populate Medication Matrix table body (#med-table-body)
    const medTableBody = document.getElementById('med-table-body');
    if (data.medications && data.medications.length > 0) {
      medTableBody.innerHTML = ''; // clear default row
      data.medications.forEach(med => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td><input type="text" name="medicine_name[]" class="form-control med-name-input" value="${med.name || ''}"></td>
          <td><input type="text" name="dose[]" class="form-control med-dose-input" value="${med.dose || ''}"></td>
          <td><input type="text" name="frequency[]" class="form-control med-freq-input" value="${med.frequency || ''}"></td>
          <td><input type="text" name="duration[]" class="form-control med-dur-input" value="${med.duration || ''}"></td>
          <td><button type="button" class="btn-icon-danger remove-row-btn"><i class="fa-solid fa-trash-can"></i></button></td>
        `;
        medTableBody.appendChild(row);
      });
    }

    return data;
  } catch (error) {
    console.error('Failed to extract prescription:', error);
  }
}
```

---

## 3. Accuracy & Handwriting Optimization Strategies

When presenting or deploying this system, consider the following key improvements for handwritten prescriptions:

1. **TrOCR Transformer Swap-in**:
   - Tesseract performs well on printed medical documents but can struggle with dense doctor handwriting.
   - For higher accuracy, swap `ocr_engine.py` to use HuggingFace `microsoft/trocr-base-stage1` or `microsoft/trocr-large-stage1`.

2. **Custom Medical Dictionary & Regex Prompt Tuning**:
   - Maintain a small labeled sample dataset of regional prescription forms to refine regex matching for local dosage formats (e.g. `BD`, `TDS`, `1-0-1`).

3. **Human-in-the-Loop Verification**:
   - The UI includes a modal verification window (`#verification-modal`) before auto-populating fields into the official EMR record.
   - This ensures the attending physician reviews, edits, and confirms extracted values, eliminating clinical error risks from OCR hallucination.
