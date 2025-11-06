"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useState, useCallback, useEffect, useRef } from "react";
import { X, Upload } from "lucide-react";

export default function HeroSection() {
  const router = useRouter();
  const [uploadOpen, setUploadOpen] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const dialogRef = useRef<HTMLDivElement>(null);

  // Handle clicks outside the dialog
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dialogRef.current &&
        !dialogRef.current.contains(event.target as Node)
      ) {
        setUploadOpen(false);
      }
    };

    if (uploadOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () =>
        document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [uploadOpen]);

  const onFiles = useCallback((selected: FileList | null) => {
    if (!selected) return;
    setFiles((prev) => [...prev, ...Array.from(selected)]);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      onFiles(e.dataTransfer.files);
    },
    [onFiles]
  );

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFiles(e.target.files);
    e.currentTarget.value = ""; // reset
  };

  const removeFile = (idx: number) =>
    setFiles((prev) => prev.filter((_, i) => i !== idx));

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") setUploadOpen(false);
    };

    if (uploadOpen) {
      document.addEventListener("keydown", handleEscape);
      return () => document.removeEventListener("keydown", handleEscape);
    }
  }, [uploadOpen]);

  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
      <div className="flex flex-col justify-center items-center text-center px-4 md:px-8">
        <h1 className="text-white font-bold text-3xl sm:text-4xl md:text-5xl lg:text-6xl max-w-[90%] sm:max-w-[600px] md:max-w-[700px] mb-6 md:mb-9 leading-tight">
          AI Platform for Teams Buried in Manual Paperwork
        </h1>

        <p className="text-white text-base sm:text-lg md:text-xl max-w-md sm:max-w-lg md:max-w-2xl mb-6 md:mb-9">
          Turn complex documents into structured insights to JSON and CSV format
        </p>

        <div className="flex gap-4 pointer-events-auto">
          <Button
            onClick={() => router.push("/signup")}
            className="w-[180px] sm:w-[220px] md:w-[250px] text-[14px] sm:text-[16px] md:text-[18px] flex justify-center"
          >
            Get Started
          </Button>

          <Button
            variant="outline"
            onClick={() => setUploadOpen(true)}
            className="w-40 sm:w-[200px]"
          >
            Upload Document
          </Button>
        </div>

        {/* Upload Modal */}
        {uploadOpen && (
          <div className="fixed inset-0 z-60 flex items-center justify-center">
            <div
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
              onClick={() => setUploadOpen(false)}
            />

            <div
              ref={dialogRef}
              className="relative z-10 w-full max-w-3xl mx-4 bg-linear-to-b from-[#0b0612] to-[#05020a] border border-neutral-800 rounded-2xl shadow-2xl p-6 pointer-events-auto"
              onClick={(e) => e.stopPropagation()} // Prevent clicks from reaching backdrop
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-neutral-800/50">
                    <Upload className="w-5 h-5 text-neutral-300" />
                  </div>
                  <div>
                    <h3 className="text-white text-2xl font-semibold">
                      Upload documents
                    </h3>
                    <p className="text-sm text-neutral-300 mt-1">
                      Drag & drop files here or click to browse. Supported: PDF,
                      PNG, JPG
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => setUploadOpen(false)}
                  className="p-2 rounded-lg hover:bg-neutral-800/50 transition-colors"
                >
                  <X className="w-5 h-5 text-neutral-400 hover:text-white" />
                </button>
              </div>

              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                className="mt-6 rounded-xl border-2 border-dashed border-neutral-700 p-6 flex flex-col items-center justify-center text-center bg-transparent"
              >
                <input
                  id="file-input"
                  type="file"
                  multiple
                  onChange={handleFileChange}
                  className="hidden"
                />
                <label htmlFor="file-input" className="cursor-pointer">
                  <div className="text-white text-lg font-medium mb-2">
                    Drop files here
                  </div>
                  <div className="text-neutral-400 mb-4">
                    or click to select files
                  </div>
                  <div className="flex gap-3 justify-center">
                    <Button asChild>
                      <span className="px-4 py-2">Browse</span>
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={() => {
                        /* placeholder */
                      }}
                    >
                      Upload
                    </Button>
                  </div>
                </label>
              </div>

              <div className="mt-6">
                <h4 className="text-white text-sm font-medium mb-2">Files</h4>
                <div className="flex flex-col gap-2 max-h-48 overflow-auto">
                  {files.length === 0 && (
                    <div className="text-neutral-500 text-sm">
                      No files selected
                    </div>
                  )}
                  {files.map((f, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between gap-4 bg-neutral-900/50 p-2 rounded-md"
                    >
                      <div className="truncate text-sm text-white">
                        {f.name}
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="text-xs text-neutral-400">
                          {(f.size / 1024).toFixed(1)} KB
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => removeFile(i)}
                        >
                          Remove
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
