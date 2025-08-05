import React, { useState, useRef } from 'react';

const ImageUpload = ({ onImageUpload, isProcessing, className = "" }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileInputChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleFileUpload = (file) => {
    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('Image too large. Please upload an image smaller than 10MB');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target.result;
      const base64 = result.split(',')[1]; // Remove data URL prefix
      
      setUploadedImage(file);
      setImagePreview(result);
      onImageUpload(base64, file.name);
    };
    reader.readAsDataURL(file);
  };

  const handleRemoveImage = () => {
    setUploadedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    onImageUpload(null);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className={`image-upload-container ${className}`}>
      {!uploadedImage ? (
        <div
          className={`image-upload-zone ${isDragOver ? 'drag-over' : ''} ${isProcessing ? 'processing' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleClick}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileInputChange}
            className="hidden-file-input"
            disabled={isProcessing}
          />
          
          <div className="upload-content">
            {isProcessing ? (
              <>
                <div className="upload-spinner"></div>
                <p className="upload-text">Processing image...</p>
                <p className="upload-subtext">Analyzing content and extracting information</p>
              </>
            ) : (
              <>
                <div className="upload-icon">
                  <span className="icon-image">🖼️</span>
                  <span className="icon-plus">+</span>
                </div>
                <p className="upload-text">
                  Drop an image here or <span className="upload-link">click to browse</span>
                </p>
                <p className="upload-subtext">
                  Supports PNG, JPG, GIF • Max 10MB
                </p>
                <div className="upload-features">
                  <div className="feature-item">
                    <span className="feature-icon">🔍</span>
                    <span>Text extraction</span>
                  </div>
                  <div className="feature-item">
                    <span className="feature-icon">🎯</span>
                    <span>Content analysis</span>
                  </div>
                  <div className="feature-item">
                    <span className="feature-icon">✨</span>
                    <span>AI enhancement</span>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      ) : (
        <div className="image-preview-container">
          <div className="image-preview-header">
            <div className="image-info">
              <span className="image-name">{uploadedImage.name}</span>
              <span className="image-size">
                {(uploadedImage.size / 1024).toFixed(1)} KB
              </span>
            </div>
            <button
              onClick={handleRemoveImage}
              className="remove-image-btn"
              disabled={isProcessing}
            >
              <span className="remove-icon">✕</span>
            </button>
          </div>
          
          <div className="image-preview">
            <img src={imagePreview} alt="Uploaded preview" className="preview-image" />
            {isProcessing && (
              <div className="processing-overlay">
                <div className="processing-spinner"></div>
                <p className="processing-text">Analyzing image...</p>
              </div>
            )}
          </div>
          
          <div className="image-status">
            {isProcessing ? (
              <div className="status-processing">
                <span className="status-icon">⏳</span>
                <span>Processing with AI vision models...</span>
              </div>
            ) : (
              <div className="status-ready">
                <span className="status-icon">✅</span>
                <span>Ready for enhancement</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;