import React, { useMemo, useState, useCallback, useRef } from 'react';
import { useFormContext, Controller } from 'react-hook-form';
import type { FieldValues, FieldPath } from 'react-hook-form';
import type { UploadFieldProps, UploadFile } from './Form.types';
import { FormErrorMessage, FormHelperText } from './Form';

/**
 * Generate unique ID for files
 */
const generateFileId = (): string => {
  return `file-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Format file size for display
 */
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * FormUpload Component
 * 
 * File upload component integrated with React Hook Form.
 * Provides drag-and-drop, multi-file support, and file preview.
 * 
 * FEATURES:
 * - Drag and drop support
 * - Multiple file upload
 * - File type/size validation
 * - File preview for images
 * - Upload progress display
 * - Cyberpunk Lab Theme styling
 * 
 * @example
 * ```tsx
 * <FormUpload
 *   name="documents"
 *   label="Upload Documents"
 *   accept=".pdf,.doc,.docx"
 *   multiple
 *   maxSize={10485760}
 *   onUpload={handleFileUpload}
 * />
 * ```
 */
export const FormUpload = <
  TFieldValues extends FieldValues = FieldValues
>({
  name,
  label,
  helperText,
  required = false,
  disabled = false,
  className = '',
  accept,
  multiple = false,
  maxSize = 5 * 1024 * 1024, // 5MB default
  maxFiles = 10,
  enableDragDrop = true,
  onUpload,
  buttonText = 'Choose Files',
  showPreview = true,
  ...props
}: UploadFieldProps<TFieldValues>) => {
  const {
    control,
    formState: { errors },
  } = useFormContext<TFieldValues>();

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState<UploadFile[]>([]);

  // Get error message for this field
  const error = useMemo(() => {
    const fieldError = errors[name];
    return fieldError?.message as string | undefined;
  }, [errors, name]);

  // Memoize wrapper class
  const wrapperClass = useMemo(() => {
    return ['form-field-wrapper', 'form-upload-wrapper', className].filter(Boolean).join(' ');
  }, [className]);

  // Memoize dropzone class
  const dropzoneClass = useMemo(() => {
    return [
      'form-upload-dropzone',
      isDragging && 'form-upload-dropzone--dragging',
      error && 'form-upload-dropzone--error',
      disabled && 'form-upload-dropzone--disabled'
    ].filter(Boolean).join(' ');
  }, [isDragging, error, disabled]);

  // Memoize label class
  const labelClass = useMemo(() => {
    return [
      'form-label',
      required && 'form-label--required'
    ].filter(Boolean).join(' ');
  }, [required]);

  // Validate file
  const validateFile = useCallback((file: File): string | null => {
    if (file.size > maxSize) {
      return `File "${file.name}" exceeds maximum size of ${formatFileSize(maxSize)}`;
    }
    
    if (accept) {
      const acceptedTypes = accept.split(',').map(t => t.trim());
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
      const fileMimeType = file.type;
      
      const isAccepted = acceptedTypes.some(type => {
        if (type.startsWith('.')) {
          return fileExtension === type.toLowerCase();
        }
        if (type.endsWith('/*')) {
          return fileMimeType.startsWith(type.replace('/*', ''));
        }
        return fileMimeType === type;
      });
      
      if (!isAccepted) {
        return `File type "${fileExtension}" is not accepted`;
      }
    }
    
    return null;
  }, [accept, maxSize]);

  // Process files
  const processFiles = useCallback(async (
    files: FileList | File[],
    currentFiles: UploadFile[],
    onChange: (files: UploadFile[]) => void
  ) => {
    const fileArray = Array.from(files);
    
    // Check max files limit
    if (currentFiles.length + fileArray.length > maxFiles) {
      alert(`Maximum ${maxFiles} files allowed`);
      return;
    }

    const newFiles: UploadFile[] = [];
    
    for (const file of fileArray) {
      const validationError = validateFile(file);
      
      if (validationError) {
        alert(validationError);
        continue;
      }
      
      const uploadFile: UploadFile = {
        id: generateFileId(),
        file,
        status: 'pending',
        previewUrl: showPreview && file.type.startsWith('image/') 
          ? URL.createObjectURL(file) 
          : undefined
      };
      
      newFiles.push(uploadFile);
    }

    const allFiles = [...currentFiles, ...newFiles];
    onChange(allFiles);
    
    // If custom upload handler provided, execute it
    if (onUpload) {
      setUploadingFiles(newFiles.map(f => ({ ...f, status: 'uploading' as const })));
      
      try {
        const uploadedFiles = await onUpload(newFiles.map(f => f.file));
        
        // Update files with upload results
        const updatedFiles = allFiles.map(f => {
          const uploaded = uploadedFiles.find(u => u.id === f.id);
          return uploaded ? { ...f, ...uploaded } : f;
        });
        
        onChange(updatedFiles);
      } catch (uploadError) {
        // Mark files as error
        const errorFiles = allFiles.map(f => ({
          ...f,
          status: 'error' as const,
          error: 'Upload failed'
        }));
        onChange(errorFiles);
      }
      
      setUploadingFiles([]);
    }
  }, [maxFiles, validateFile, showPreview, onUpload]);

  // Handle drag events
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    if (!enableDragDrop || disabled) return;
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, [enableDragDrop, disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    if (!enableDragDrop || disabled) return;
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, [enableDragDrop, disabled]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    if (!enableDragDrop || disabled) return;
    e.preventDefault();
    e.stopPropagation();
  }, [enableDragDrop, disabled]);

  // Handle file selection
  const handleFileSelect = useCallback((
    e: React.ChangeEvent<HTMLInputElement>,
    currentFiles: UploadFile[],
    onChange: (files: UploadFile[]) => void
  ) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      processFiles(files, currentFiles, onChange);
    }
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [processFiles]);

  // Handle drop
  const handleDrop = useCallback((
    e: React.DragEvent,
    currentFiles: UploadFile[],
    onChange: (files: UploadFile[]) => void
  ) => {
    if (!enableDragDrop || disabled) return;
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      processFiles(files, currentFiles, onChange);
    }
  }, [enableDragDrop, disabled, processFiles]);

  // Remove file
  const handleRemoveFile = useCallback((
    fileId: string,
    currentFiles: UploadFile[],
    onChange: (files: UploadFile[]) => void
  ) => {
    const file = currentFiles.find(f => f.id === fileId);
    if (file?.previewUrl) {
      URL.revokeObjectURL(file.previewUrl);
    }
    onChange(currentFiles.filter(f => f.id !== fileId));
  }, []);

  // Open file dialog
  const openFileDialog = useCallback(() => {
    if (!disabled) {
      fileInputRef.current?.click();
    }
  }, [disabled]);

  return (
    <div className={wrapperClass}>
      {label && (
        <label className={labelClass}>
          {label}
          {required && <span aria-hidden="true"> *</span>}
        </label>
      )}

      <Controller
        name={name}
        control={control}
        defaultValue={[] as UploadFile[]}
        render={({ field }) => {
          const currentFiles = field.value || [];
          
          return (
            <div className="form-upload-container">
              <div
                className={dropzoneClass}
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDragOver={handleDragOver}
                onDrop={(e) => handleDrop(e, currentFiles, field.onChange)}
                onClick={openFileDialog}
                role="button"
                tabIndex={disabled ? -1 : 0}
                aria-disabled={disabled}
                aria-invalid={!!error}
                aria-required={required}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    openFileDialog();
                  }
                }}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept={accept}
                  multiple={multiple}
                  disabled={disabled}
                  onChange={(e) => handleFileSelect(e, currentFiles, field.onChange)}
                  style={{ display: 'none' }}
                  aria-hidden="true"
                />
                
                <div className="form-upload-icon">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                </div>
                
                <p className="form-upload-text">
                  {isDragging ? 'Drop files here' : 'Drag and drop files here, or click to select'}
                </p>
                
                <button
                  type="button"
                  className="form-upload-button"
                  disabled={disabled}
                  onClick={(e) => {
                    e.stopPropagation();
                    openFileDialog();
                  }}
                >
                  {buttonText}
                </button>
                
                {maxSize && (
                  <p className="form-upload-hint">
                    Max file size: {formatFileSize(maxSize)}
                    {multiple && maxFiles && ` • Max files: ${maxFiles}`}
                  </p>
                )}
              </div>

              {/* File list */}
              {showPreview && currentFiles.length > 0 && (
                <ul className="form-upload-list">
                  {currentFiles.map((file) => (
                    <li key={file.id} className="form-upload-item">
                      {file.previewUrl ? (
                        <img
                          src={file.previewUrl}
                          alt={file.file.name}
                          className="form-upload-preview"
                        />
                      ) : (
                        <div className="form-upload-file-icon">
                          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
                            <polyline points="13 2 13 9 20 9" />
                          </svg>
                        </div>
                      )}
                      
                      <div className="form-upload-item-info">
                        <span className="form-upload-item-name">{file.file.name}</span>
                        <span className="form-upload-item-size">{formatFileSize(file.file.size)}</span>
                        {file.status === 'uploading' && (
                          <div className="form-upload-progress">
                            <div 
                              className="form-upload-progress-bar" 
                              style={{ width: `${file.progress || 0}%` }}
                            />
                          </div>
                        )}
                        {file.status === 'error' && (
                          <span className="form-upload-error">{file.error}</span>
                        )}
                      </div>
                      
                      <button
                        type="button"
                        className="form-upload-remove"
                        onClick={() => handleRemoveFile(file.id, currentFiles, field.onChange)}
                        aria-label={`Remove ${file.file.name}`}
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <line x1="18" y1="6" x2="6" y2="18" />
                          <line x1="6" y1="6" x2="18" y2="18" />
                        </svg>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          );
        }}
      />

      <FormErrorMessage error={error} className="form-error-message" />
      {!error && <FormHelperText text={helperText} className="form-helper-text" />}
    </div>
  );
};

FormUpload.displayName = 'FormUpload';

/**
 * Memoized FormUpload component for performance
 */
const MemoizedFormUpload = React.memo(FormUpload) as typeof FormUpload;

export default MemoizedFormUpload;
