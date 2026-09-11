import React, { useState, useEffect, useRef } from 'react';
import {
  Folder,
  UploadCloud,
  FileText,
  Image as ImageIcon,
  Download,
  Trash2,
  CheckCircle,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import { uploadEvidence, listCaseEvidence, deleteEvidence, BASE_URL } from '../../services/api';

export default function EvidenceUploader({ caseId, readOnly = false, onEvidenceChanged }) {
  const [evidenceList, setEvidenceList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const [description, setDescription] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const fetchEvidence = async () => {
    if (!caseId) return;
    try {
      setLoading(true);
      const data = await listCaseEvidence(caseId);
      setEvidenceList(data || []);
    } catch (err) {
      console.error('Failed to load evidence:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvidence();
  }, [caseId]);

  const handleFiles = async (files) => {
    if (!files || files.length === 0) return;
    setError(null);
    setSuccessMsg(null);
    setUploading(true);

    try {
      const formData = new FormData();
      for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
      }
      if (description) {
        formData.append('description', description);
      }

      await uploadEvidence(caseId, formData);
      setSuccessMsg(`Successfully uploaded ${files.length} evidence file(s).`);
      setDescription('');
      if (fileInputRef.current) fileInputRef.current.value = '';
      await fetchEvidence();
      if (onEvidenceChanged) onEvidenceChanged();
    } catch (err) {
      setError(err.message || 'Failed to upload evidence');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (readOnly) return;
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleDelete = async (evidenceId) => {
    if (!window.confirm('Are you sure you want to remove this evidence file from chain of custody?')) return;
    try {
      await deleteEvidence(evidenceId);
      await fetchEvidence();
      if (onEvidenceChanged) onEvidenceChanged();
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const formatBytes = (bytes) => {
    if (!bytes || bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  return (
    <div style={{ background: '#FFFFFF', borderRadius: 8, border: '1px solid #E2E8F0', padding: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <h3 style={{ margin: 0, fontSize: 15, fontWeight: 800, color: '#0F172A', display: 'flex', alignItems: 'center', gap: 8 }}>
            <Folder size={18} color="#003366" />
            Case Evidence &amp; Forensic Document Repository
          </h3>
          <p style={{ margin: '3px 0 0', fontSize: 12, color: '#64748B' }}>
            Chain-of-custody compliant document repository, site photographs, medical certificates &amp; FIR attachments.
          </p>
        </div>
        <span style={{
          fontSize: 11,
          fontWeight: 700,
          background: '#EFF6FF',
          color: '#003366',
          padding: '4px 10px',
          borderRadius: 4,
          border: '1px solid #BFDBFE',
        }}>
          {evidenceList.length} Item(s) Attached
        </span>
      </div>

      {error && (
        <div style={{ background: '#FEF2F2', border: '1px solid #FECACA', color: '#B91C1C', padding: '10px 14px', borderRadius: 6, fontSize: 12, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
          <AlertCircle size={15} />
          {error}
        </div>
      )}

      {successMsg && (
        <div style={{ background: '#F0FDF4', border: '1px solid #BBF7D0', color: '#15803D', padding: '10px 14px', borderRadius: 6, fontSize: 12, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
          <CheckCircle size={15} />
          {successMsg}
        </div>
      )}

      {/* Upload Dropzone */}
      {!readOnly && (
        <div style={{ marginBottom: 20 }}>
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            style={{
              border: `2px dashed ${dragOver ? '#003366' : '#CBD5E1'}`,
              borderRadius: 8,
              padding: '24px 16px',
              textAlign: 'center',
              background: dragOver ? '#EFF6FF' : '#F8FAFC',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            <input
              type="file"
              ref={fileInputRef}
              multiple
              style={{ display: 'none' }}
              onChange={(e) => handleFiles(e.target.files)}
            />
            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 8 }}>
              <UploadCloud size={32} color="#003366" />
            </div>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#003366' }}>
              Drag &amp; Drop Evidence Files Here, or Click to Browse Local Storage
            </div>
            <div style={{ fontSize: 11, color: '#64748B', marginTop: 4 }}>
              Supports Images (JPG, PNG), Documents (PDF, DOCX), Forensic Reports, Site Photos, Audio/Video Recordings
            </div>
          </div>

          <div style={{ display: 'flex', gap: 10, marginTop: 10 }}>
            <input
              type="text"
              placeholder="Add chain-of-custody description or forensic note (optional)..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              style={{
                flex: 1,
                padding: '9px 12px',
                fontSize: 12,
                border: '1px solid #CBD5E1',
                borderRadius: 6,
                background: '#FFFFFF',
              }}
            />
          </div>

          {uploading && (
            <div style={{ marginTop: 10, fontSize: 12, color: '#003366', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6 }}>
              <Loader2 size={14} className="animate-spin" /> Uploading files to secure repository...
            </div>
          )}
        </div>
      )}

      {/* Evidence Gallery / File List */}
      <div>
        <div style={{ fontSize: 12, fontWeight: 800, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: 12 }}>
          Attached Evidence Dockets
        </div>

        {loading ? (
          <div style={{ fontSize: 12, color: '#64748B', padding: 16, textAlign: 'center' }}>Loading evidence files...</div>
        ) : evidenceList.length === 0 ? (
          <div style={{ fontSize: 12, color: '#94A3B8', padding: '20px 16px', textAlign: 'center', background: '#F8FAFC', borderRadius: 6, border: '1px dashed #CBD5E1' }}>
            No evidence files attached yet. Investigating officers can attach site photos, medical certificates, and transcripts here.
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 12 }}>
            {evidenceList.map((ev) => {
              const isImage = ev.file_type?.startsWith('image/') || ev.file_name.match(/\.(jpg|jpeg|png|webp|gif)$/i);
              const downloadUrl = `${BASE_URL}/api/evidence/${ev.id}/download`;

              return (
                <div
                  key={ev.id}
                  style={{
                    border: '1px solid #E2E8F0',
                    borderRadius: 8,
                    padding: 12,
                    background: '#FFFFFF',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.02)',
                  }}
                >
                  <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                    <div style={{
                      width: 42,
                      height: 42,
                      borderRadius: 6,
                      background: isImage ? '#EFF6FF' : '#F1F5F9',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                      overflow: 'hidden',
                    }}>
                      {isImage ? (
                        <img
                          src={`${BASE_URL}/${ev.file_path}`}
                          alt={ev.file_name}
                          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                          onError={(e) => { e.target.style.display = 'none'; }}
                        />
                      ) : (
                        <FileText size={20} color="#003366" />
                      )}
                    </div>

                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 12, fontWeight: 700, color: '#0F172A', wordBreak: 'break-all', lineHeight: 1.3 }}>
                        {ev.file_name}
                      </div>
                      <div style={{ fontSize: 10, color: '#64748B', marginTop: 2, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        <span>{formatBytes(ev.file_size)}</span>
                        <span>&bull;</span>
                        <span style={{ textTransform: 'uppercase', fontWeight: 700, color: '#003366' }}>
                          Tier: {ev.tier_level || 'Field'}
                        </span>
                      </div>
                      {ev.description && (
                        <div style={{ fontSize: 11, color: '#334155', marginTop: 4, fontStyle: 'italic' }}>
                          "{ev.description}"
                        </div>
                      )}
                    </div>
                  </div>

                  <div style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginTop: 10,
                    paddingTop: 8,
                    borderTop: '1px solid #F1F5F9',
                  }}>
                    <span style={{ fontSize: 10, color: '#94A3B8' }}>
                      {ev.uploaded_at ? new Date(ev.uploaded_at).toLocaleDateString('en-IN') : 'Recent'}
                    </span>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <a
                        href={downloadUrl}
                        target="_blank"
                        rel="noreferrer"
                        style={{
                          fontSize: 11,
                          fontWeight: 700,
                          color: '#003366',
                          textDecoration: 'none',
                          padding: '4px 8px',
                          background: '#EFF6FF',
                          borderRadius: 4,
                          border: '1px solid #BFDBFE',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 4,
                        }}
                      >
                        <Download size={11} /> Download
                      </a>
                      {!readOnly && (
                        <button
                          type="button"
                          onClick={() => handleDelete(ev.id)}
                          style={{
                            fontSize: 11,
                            fontWeight: 700,
                            color: '#DC2626',
                            background: '#FEF2F2',
                            border: '1px solid #FECACA',
                            padding: '4px 8px',
                            borderRadius: 4,
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 4,
                          }}
                        >
                          <Trash2 size={11} /> Delete
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
