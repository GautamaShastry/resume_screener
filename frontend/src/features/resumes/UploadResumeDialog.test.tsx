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

test("double-clicking Upload sends only one request", async () => {
  const { http, HttpResponse, delay } = await import("msw");
  const { API, server } = await import("../../test/server");
  let posts = 0;
  server.use(
    http.post(`${API}/api/resumes`, async () => {
      posts += 1;
      await delay(200);
      return HttpResponse.json(
        { code: "VALIDATION", message: "nope", details: {} },
        { status: 422 },
      );
    }),
  );
  renderWithProviders(<UploadResumeDialog trigger="Upload résumé" />);
  await userEvent.click(screen.getByRole("button", { name: "Upload résumé" }));
  await userEvent.upload(
    screen.getByLabelText("Résumé file"),
    new File(["%PDF-1.4"], "cv.pdf", { type: "application/pdf" }),
  );
  const upload = screen.getByRole("button", { name: "Upload" });
  await userEvent.dblClick(upload);
  await screen.findByRole("alert");
  expect(posts).toBe(1);
});
