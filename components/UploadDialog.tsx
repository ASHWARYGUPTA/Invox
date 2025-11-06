import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { X, Upload } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTrigger,
} from "@/components/ui/dialog";
import { DialogTitle } from "@radix-ui/react-dialog";

export function DialogDemo() {
  const [files, setFiles] = useState<File[]>([]);

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

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Upload Documents</Button>
      </DialogTrigger>
      <DialogContent className="max-w-3xl bg-linear-to-b from-[#0b0612] to-[#05020a] border-neutral-800">
        <DialogTitle className="hidden"></DialogTitle>
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
                Drag & drop files here or click to browse. Supported: PDF, PNG,
                JPG
              </p>
            </div>
          </div>

          <DialogTrigger asChild>
            <button className="p-2 rounded-lg hover:bg-neutral-800/50 transition-colors">
              <X className="w-5 h-5 text-neutral-400 hover:text-white" />
            </button>
          </DialogTrigger>
        </div>

        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          className="mt-6 rounded-xl border-2 border-dashed border-neutral-700 p-6 flex flex-col items-center justify-center text-center bg-transparent"
        >
          <input
            id="file-input-dashboard"
            type="file"
            multiple
            onChange={handleFileChange}
            className="hidden"
          />
          <label htmlFor="file-input-dashboard" className="cursor-pointer">
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
              <div className="text-neutral-500 text-sm">No files selected</div>
            )}
            {files.map((f, i) => (
              <div
                key={i}
                className="flex items-center justify-between gap-4 bg-neutral-900/50 p-2 rounded-md"
              >
                <div className="truncate text-sm text-white">{f.name}</div>
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
      </DialogContent>
    </Dialog>
  );
}
