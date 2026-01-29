import React, { useState, useCallback } from "react";
import {
  Upload,
  CheckCircle,
  AlertCircle,
  Clock,
  Download,
  Eye,
  ArrowRight,
} from "lucide-react";
import { useDataImport } from "../context/DataImportContext";
import type { ImportType } from "../context/DataImportContext";
import Breadcrumbs from "../components/common/Breadcrumbs";

type ImportStep = "upload" | "preview" | "validate" | "import" | "complete";

const DataImport: React.FC = () => {
  const {
    currentJob,
    isLoading,
    error,
    uploadFile,
    validateImport,
    startImport,
    clearCurrentJob,
  } = useDataImport();

  const [step, setStep] = useState<ImportStep>("upload");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [importType, setImportType] = useState<ImportType>("SALES_DATA");
  const [proceedWithErrors, setProceedWithErrors] = useState(false);
  const [preview, setPreview] = useState<any[]>([]);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const importTypeDescriptions = {
    SALES_DATA: {
      title: "Sales Data",
      description: "Import sales history with prices and quantities",
      columns:
        "date, market_name, commodity_name, price, quantity, unit, grade",
      example: "2026-01-29, Azadpur Market, Wheat, 2500.00, 100, kg, A-grade",
    },
    MARKET_PRICES: {
      title: "Market Prices",
      description: "Import market price data from Agmarknet or other sources",
      columns:
        "date, market_name, commodity_name, min_price, max_price, modal_price, arrival_quantity",
      example: "2026-01-29, Mumbai Market, Rice, 2400.00, 2600.00, 2500.00, 1000",
    },
    INVENTORY: {
      title: "Inventory Data",
      description: "Import inventory levels and movements",
      columns:
        "date, market_name, commodity_name, quantity_in_stock, quantity_sold, quantity_damaged, unit, notes",
      example: "2026-01-29, Azadpur Market, Potato, 5000, 1200, 50, kg, Good condition",
    },
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.name.endsWith(".csv")) {
        setUploadError("Please select a CSV file");
        return;
      }
      if (file.size > 50 * 1024 * 1024) {
        setUploadError("File size must be less than 50MB");
        return;
      }
      setSelectedFile(file);
      setUploadError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadError("Please select a file");
      return;
    }

    try {
      const response = await uploadFile(selectedFile, importType);
      setPreview(response.preview);
      setStep("preview");
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Upload failed");
    }
  };

  const handleValidate = async () => {
    if (!currentJob) return;

    try {
      const job = await validateImport(currentJob.job_id);
      setStep("validate");
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Validation failed");
    }
  };

  const handleStartImport = async () => {
    if (!currentJob) return;

    try {
      const job = await startImport(currentJob.job_id, proceedWithErrors);
      setStep("import");
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Import failed");
    }
  };

  const handleReset = () => {
    clearCurrentJob();
    setStep("upload");
    setSelectedFile(null);
    setPreview([]);
    setUploadError(null);
    setProceedWithErrors(false);
  };

  const renderUploadStep = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {(Object.keys(importTypeDescriptions) as ImportType[]).map((type) => (
          <label key={type} className="cursor-pointer">
            <input
              type="radio"
              name="importType"
              value={type}
              checked={importType === type}
              onChange={(e) => setImportType(e.target.value as ImportType)}
              className="sr-only"
            />
            <div
              className={`p-4 rounded-lg border-2 transition-all ${
                importType === type
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-200 bg-white hover:border-blue-300"
              }`}
            >
              <div className="font-semibold text-gray-900">
                {importTypeDescriptions[type].title}
              </div>
              <div className="text-sm text-gray-600 mt-1">
                {importTypeDescriptions[type].description}
              </div>
            </div>
          </label>
        ))}
      </div>

      {/* File Upload Area */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-400 transition-colors">
        <div className="flex justify-center mb-4">
          <Upload className="w-12 h-12 text-gray-400" />
        </div>
        <p className="text-gray-600 mb-4">
          Drag and drop your CSV file here, or click to select
        </p>
        <input
          type="file"
          accept=".csv"
          onChange={handleFileSelect}
          className="hidden"
          id="file-input"
        />
        <label htmlFor="file-input">
          <button
            onClick={() => document.getElementById("file-input")?.click()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Select File
          </button>
        </label>

        {selectedFile && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-800">✓ {selectedFile.name}</p>
            <p className="text-sm text-green-600">
              {(selectedFile.size / 1024).toFixed(2)} KB
            </p>
          </div>
        )}
      </div>

      {/* File Format Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="font-semibold text-blue-900 mb-2">Required Columns:</p>
        <code className="text-sm text-blue-800 block font-mono mb-3">
          {importTypeDescriptions[importType].columns}
        </code>
        <p className="font-semibold text-blue-900 mb-2">Example:</p>
        <code className="text-sm text-blue-800 block font-mono">
          {importTypeDescriptions[importType].example}
        </code>
      </div>

      {uploadError && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="text-red-800">{uploadError}</div>
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!selectedFile || isLoading}
        className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-semibold flex items-center justify-center gap-2"
      >
        {isLoading ? "Uploading..." : "Upload & Preview"}
        <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  );

  const renderPreviewStep = () => (
    <div className="space-y-6">
      <div>
        <h3 className="font-semibold text-gray-900 mb-3">Data Preview</h3>
        <div className="overflow-x-auto border border-gray-200 rounded-lg">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                {preview[0] &&
                  Object.keys(preview[0]).map((key) => (
                    <th
                      key={key}
                      className="px-4 py-2 text-left font-semibold text-gray-900"
                    >
                      {key}
                    </th>
                  ))}
              </tr>
            </thead>
            <tbody>
              {preview.slice(0, 5).map((row, idx) => (
                <tr key={idx} className="border-b border-gray-100">
                  {Object.values(row).map((value: any, colIdx) => (
                    <td key={colIdx} className="px-4 py-2 text-gray-700">
                      {String(value)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Showing first 5 of {currentJob?.stats?.total_records || 0} records
        </p>
      </div>

      <div className="flex gap-3">
        <button
          onClick={() => setStep("upload")}
          className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Back
        </button>
        <button
          onClick={handleValidate}
          disabled={isLoading}
          className="flex-1 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors font-semibold flex items-center justify-center gap-2"
        >
          {isLoading ? "Validating..." : "Validate Data"}
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );

  const renderValidateStep = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-gray-600 text-sm">Total Records</div>
          <div className="text-2xl font-bold text-gray-900">
            {currentJob?.stats?.total_records || 0}
          </div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <div className="text-green-700 text-sm">Valid Records</div>
          <div className="text-2xl font-bold text-green-900">
            {currentJob?.stats?.valid_records || 0}
          </div>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
          <div className="text-yellow-700 text-sm">Invalid Records</div>
          <div className="text-2xl font-bold text-yellow-900">
            {currentJob?.stats?.invalid_records || 0}
          </div>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
          <div className="text-orange-700 text-sm">Duplicates</div>
          <div className="text-2xl font-bold text-orange-900">
            {currentJob?.stats?.duplicate_records || 0}
          </div>
        </div>
      </div>

      {currentJob?.stats?.validation_errors && currentJob.stats.validation_errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <h4 className="font-semibold text-red-900">
              {currentJob.stats.validation_errors.length} Validation Errors
            </h4>
          </div>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {currentJob.stats.validation_errors.slice(0, 10).map((err, idx) => (
              <div key={idx} className="text-sm p-2 bg-white rounded border border-red-100">
                <div className="text-red-900 font-mono">
                  Row {err.row}: {err.error_message}
                </div>
                {err.suggestion && (
                  <div className="text-red-700 text-xs mt-1">
                    💡 {err.suggestion}
                  </div>
                )}
              </div>
            ))}
          </div>
          <label className="flex items-center gap-2 mt-4 p-2 bg-white rounded">
            <input
              type="checkbox"
              checked={proceedWithErrors}
              onChange={(e) => setProceedWithErrors(e.target.checked)}
              className="w-4 h-4"
            />
            <span className="text-red-900">
              Proceed with import despite errors
            </span>
          </label>
        </div>
      )}

      <div className="flex gap-3">
        <button
          onClick={() => setStep("preview")}
          className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Back
        </button>
        <button
          onClick={handleStartImport}
          disabled={isLoading || (currentJob?.stats?.invalid_records || 0) > 0 && !proceedWithErrors}
          className="flex-1 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors font-semibold flex items-center justify-center gap-2"
        >
          {isLoading ? "Starting..." : "Start Import"}
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );

  const renderImportStep = () => (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
            <Clock className="w-6 h-6 text-blue-600 animate-spin" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">
              {currentJob?.status === "COMPLETED"
                ? "Import Completed"
                : "Importing Data"}
            </h3>
            <p className="text-sm text-gray-600">
              {currentJob?.status === "COMPLETED"
                ? "All data has been successfully imported"
                : "Please wait while we import your data..."}
            </p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Progress</span>
            <span className="text-sm font-bold text-gray-900">
              {currentJob?.progress_percentage || 0}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-500"
              style={{
                width: `${currentJob?.progress_percentage || 0}%`,
              }}
            />
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gray-50 p-3 rounded">
            <div className="text-xs text-gray-600">Inserted</div>
            <div className="text-lg font-bold text-gray-900">
              {currentJob?.stats?.inserted_records || 0}
            </div>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <div className="text-xs text-gray-600">Skipped</div>
            <div className="text-lg font-bold text-gray-900">
              {currentJob?.stats?.skipped_records || 0}
            </div>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <div className="text-xs text-gray-600">Duplicates</div>
            <div className="text-lg font-bold text-gray-900">
              {currentJob?.stats?.duplicate_records || 0}
            </div>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <div className="text-xs text-gray-600">Time Remaining</div>
            <div className="text-lg font-bold text-gray-900">
              {currentJob?.estimated_time_remaining
                ? `${Math.ceil(currentJob.estimated_time_remaining)}s`
                : "−"}
            </div>
          </div>
        </div>
      </div>

      {currentJob?.status === "COMPLETED" && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex gap-3 items-start">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div className="text-green-800">
            <p className="font-semibold">Import Successful!</p>
            <p className="text-sm mt-1">
              {currentJob.stats?.inserted_records || 0} records have been added
              to the database.
            </p>
          </div>
        </div>
      )}

      {currentJob?.status === "FAILED" && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex gap-3 items-start">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="text-red-800">
            <p className="font-semibold">Import Failed</p>
            <p className="text-sm mt-1">{currentJob.error_message}</p>
          </div>
        </div>
      )}

      {currentJob?.status === "COMPLETED" && (
        <button
          onClick={handleReset}
          className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
        >
          Import Another File
        </button>
      )}
    </div>
  );

  const renderContent = () => {
    switch (step) {
      case "upload":
        return renderUploadStep();
      case "preview":
        return renderPreviewStep();
      case "validate":
        return renderValidateStep();
      case "import":
        return renderImportStep();
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-16 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <Breadcrumbs
            items={[
              { label: "Home", href: "/" },
              { label: "Data Import", href: "/data/import" },
            ]}
          />
          <h1 className="text-3xl font-bold text-gray-900 mt-2">Import Data</h1>
          <p className="text-gray-600 mt-1">
            Upload CSV files to import sales, market price, or inventory data
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Step Indicators */}
        <div className="flex gap-4 mb-8">
          {(
            [
              { key: "upload", label: "Upload" },
              { key: "preview", label: "Preview" },
              { key: "validate", label: "Validate" },
              { key: "import", label: "Import" },
            ] as const
          ).map((s, idx, arr) => (
            <React.Fragment key={s.key}>
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-colors ${
                    arr.findIndex((x) => x.key === step) >= idx
                      ? "bg-blue-600 text-white"
                      : "bg-gray-200 text-gray-600"
                  }`}
                >
                  {idx + 1}
                </div>
                <label className="text-xs font-semibold text-gray-600 mt-2 text-center">
                  {s.label}
                </label>
              </div>
              {idx < arr.length - 1 && (
                <div
                  className={`flex-1 h-1 mt-5 ${
                    arr.findIndex((x) => x.key === step) > idx
                      ? "bg-blue-600"
                      : "bg-gray-200"
                  }`}
                />
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg border border-gray-200 p-8">
          {renderContent()}
        </div>
      </div>
    </div>
  );
};

export default DataImport;
