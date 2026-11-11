import * as Dialog from "@radix-ui/react-dialog";
import { useState, type ReactNode } from "react";

interface Props {
  trigger: string;
  title: string;
  description: ReactNode;
  confirmLabel: string;
  onConfirm: () => Promise<void>;
  requireText?: string;
}

export function ConfirmDialog({
  trigger,
  title,
  description,
  confirmLabel,
  onConfirm,
  requireText,
}: Props) {
  const [open, setOpen] = useState(false);
  const [typed, setTyped] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const blocked = busy || (requireText !== undefined && typed !== requireText);
  return (
    <Dialog.Root
      open={open}
      onOpenChange={(o) => {
        setOpen(o);
        setTyped("");
        setError(null);
      }}
    >
      <Dialog.Trigger asChild>
        <button className="rounded-md border border-red-300 px-3 py-1.5 text-sm text-red-700">
          {trigger}
        </button>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/30" />
        <Dialog.Content className="fixed left-1/2 top-1/2 w-[min(28rem,92vw)] -translate-x-1/2 -translate-y-1/2 space-y-3 rounded-lg bg-white p-5 shadow-lg">
          <Dialog.Title className="text-lg font-semibold">{title}</Dialog.Title>
          <Dialog.Description className="text-sm text-slate-700">{description}</Dialog.Description>
          {requireText !== undefined && (
            <div>
              <label htmlFor="confirm-text" className="block text-sm font-medium">
                Type {requireText} to confirm
              </label>
              <input
                id="confirm-text"
                value={typed}
                onChange={(e) => setTyped(e.target.value)}
                className="mt-1 w-full rounded-md border px-3 py-2"
              />
            </div>
          )}
          {error && (
            <p role="alert" className="text-sm text-red-700">
              {error}
            </p>
          )}
          <div className="flex justify-end gap-2">
            <Dialog.Close asChild>
              <button className="rounded-md border px-3 py-1.5 text-sm">Cancel</button>
            </Dialog.Close>
            <button
              disabled={blocked}
              onClick={async () => {
                setBusy(true);
                try {
                  await onConfirm();
                  setOpen(false);
                } catch (err) {
                  setError((err as Error).message);
                } finally {
                  setBusy(false);
                }
              }}
              className="rounded-md bg-red-700 px-3 py-1.5 text-sm text-white disabled:opacity-50"
            >
              {confirmLabel}
            </button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
