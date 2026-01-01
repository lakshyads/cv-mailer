import { useState } from 'react';
import { Button } from '@/components/atoms/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/atoms/ui/Card';
import { X, Check } from 'lucide-react';
import type { Recruiter } from '@/types';

interface RecruiterSelectionDialogProps {
  recruiters: Recruiter[];
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (selectedRecruiterIds: number[]) => void;
  title?: string;
  confirmLabel?: string;
}

/**
 * Dialog for selecting recruiters for follow-up emails.
 */
export function RecruiterSelectionDialog({
  recruiters,
  isOpen,
  onClose,
  onConfirm,
  title = 'Select Recruiters',
  confirmLabel = 'Send Follow-up',
}: RecruiterSelectionDialogProps) {
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());

  if (!isOpen) return null;

  const handleToggle = (recruiterId: number) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(recruiterId)) {
      newSelected.delete(recruiterId);
    } else {
      newSelected.add(recruiterId);
    }
    setSelectedIds(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedIds.size === recruiters.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(recruiters.map((r) => r.id)));
    }
  };

  const handleConfirm = () => {
    if (selectedIds.size === 0) {
      onConfirm([]); // Send to all if none selected
    } else {
      onConfirm(Array.from(selectedIds));
    }
    setSelectedIds(new Set());
    onClose();
  };

  const handleCancel = () => {
    setSelectedIds(new Set());
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <Card className="w-full max-w-md mx-4">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>{title}</CardTitle>
            <Button variant="ghost" size="sm" onClick={handleCancel} className="h-8 w-8 p-0">
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-sm text-muted-foreground">
            Select which recruiters should receive the follow-up email. If none are selected, the
            follow-up will be sent to all recruiters.
          </div>

          <div className="border rounded-lg divide-y max-h-64 overflow-y-auto">
            <div className="p-2 bg-muted/30">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleSelectAll}
                className="w-full justify-start"
              >
                <Check
                  className={`h-4 w-4 mr-2 ${
                    selectedIds.size === recruiters.length ? 'opacity-100' : 'opacity-0'
                  }`}
                />
                Select All ({recruiters.length})
              </Button>
            </div>
            {recruiters.map((recruiter) => {
              const isSelected = selectedIds.has(recruiter.id);
              return (
                <div
                  key={recruiter.id}
                  className={`p-3 cursor-pointer hover:bg-muted/50 transition-colors ${
                    isSelected ? 'bg-primary/10' : ''
                  }`}
                  onClick={() => handleToggle(recruiter.id)}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`h-5 w-5 rounded border-2 flex items-center justify-center ${
                        isSelected
                          ? 'bg-primary border-primary'
                          : 'border-muted-foreground/30'
                      }`}
                    >
                      {isSelected && <Check className="h-3 w-3 text-primary-foreground" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm">{recruiter.name || 'Unknown'}</p>
                      <p className="text-xs text-muted-foreground truncate">{recruiter.email}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex gap-2 justify-end pt-2">
            <Button variant="outline" onClick={handleCancel}>
              Cancel
            </Button>
            <Button onClick={handleConfirm}>
              {confirmLabel} {selectedIds.size > 0 && `(${selectedIds.size})`}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

