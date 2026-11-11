import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithProviders } from "../../test/render";
import { UploadResumeDialog } from "./UploadResumeDialog";

test("rejects files over 5 MB without calling the API", async () => {
  renderWithProviders(<UploadResumeDialog trigger="Upload résumé" />);
  await userEvent.click(screen.getByRole("button", { name: "Upload résumé" }));
  const big = new File([new Uint8Array(5 * 1024 * 1024 + 1)], "cv.pdf", {
    type: "application/pdf",
  });
  await userEvent.upload(screen.getByLabelText("Résumé file"), big);
  expect(screen.getByRole("alert")).toHaveTextContent("larger than 5 MB");
  await userEvent.click(screen.getByRole("button", { name: "Upload" }));
  expect(screen.getByRole("alert")).toHaveTextContent("Choose a file");
});

test("rejects other file types", async () => {
  renderWithProviders(<UploadResumeDialog trigger="Upload résumé" />);
  await userEvent.click(screen.getByRole("button", { name: "Upload résumé" }));
  await userEvent.upload(
    screen.getByLabelText("Résumé file"),
    new File(["hi"], "cv.txt", { type: "text/plain" }),
    { applyAccept: false },
  );
  expect(screen.getByRole("alert")).toHaveTextContent("PDF or DOCX");
});
