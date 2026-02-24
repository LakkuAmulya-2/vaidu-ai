import { useRef, useState } from 'react';
import Button from './Button';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  accept?: string;
  maxSize?: number; // in MB
  label?: string;
}

const FileUpload = ({
  onFileSelect,
  accept = 'image/jpeg,image/png',
  maxSize = 10,
  label = 'ఫైల్‌ను ఎంచుకోండి'
}: FileUploadProps) => {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string>('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateFile = (file: File): boolean => {
    setError('');

    if (!file.type.startsWith('image/')) {
      setError('దయచేసి చిత్రం ఫైల్‌ను ఎంచుకోండి');
      return false;
    }

    const sizeInMB = file.size / (1024 * 1024);
    if (sizeInMB > maxSize) {
      setError(`ఫైల్ సైజ్ ${maxSize}MB కంటే తక్కువగా ఉండాలి`);
      return false;
    }

    return true;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) {
        onFileSelect(file);
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (validateFile(file)) {
        onFileSelect(file);
      }
    }
  };

  const handleClick = () => {
    inputRef.current?.click();
  };

  return (
    <div className="w-full">
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
          dragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleChange}
          className="hidden"
        />
        <div className="space-y-2">
          <div className="text-4xl">📷</div>
          <p className="text-gray-600">
            {label}
          </p>
          <p className="text-sm text-gray-500">
            లేదా ఇక్కడ ఫైల్‌ను డ్రాగ్ చేయండి
          </p>
          <p className="text-xs text-gray-400">
            గరిష్ట సైజు: {maxSize}MB (JPG, PNG)
          </p>
        </div>
      </div>
      {error && (
        <p className="mt-2 text-sm text-red-600 text-center">{error}</p>
      )}
    </div>
  );
};

export default FileUpload;