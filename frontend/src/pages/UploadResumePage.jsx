import UploadFileIcon from "@mui/icons-material/UploadFile";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client.js";

const ACCEPTED = [".pdf", ".docx"];

export default function UploadResumePage() {
  const [file, setFile] = useState(null);
  const [name, setName] = useState("");
  const [location, setLocation] = useState("");
  const [grade, setGrade] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  function pickFile(selected) {
    setResult(null);
    setError("");
    if (!selected) return;
    const ok = ACCEPTED.some((ext) => selected.name.toLowerCase().endsWith(ext));
    if (!ok) {
      setError("Only PDF or DOCX resumes are supported.");
      setFile(null);
      return;
    }
    setFile(selected);
    // Fall back to the filename (minus extension) so the name field is rarely empty.
    if (!name) setName(selected.name.replace(/\.(pdf|docx)$/i, "").replace(/[_-]+/g, " "));
  }

  async function submit(event) {
    event.preventDefault();
    if (!file || !name.trim()) {
      setError("A resume file and a name are both required.");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("name", name.trim());
      form.append("location", location.trim());
      form.append("grade", grade.trim());
      const { data } = await client.post("/uploadResume", form);
      setResult(data);
      setFile(null);
      setName("");
      setLocation("");
      setGrade("");
    } catch (err) {
      setError(err?.response?.data?.detail || "Upload failed. Check that the backend is running.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        Upload a resume
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        PDF or DOCX. Skills, certifications, projects and years of experience are extracted
        automatically, and the new profile becomes searchable straight away.
      </Typography>

      <Card variant="outlined">
        <CardContent>
          <form onSubmit={submit}>
            <Stack spacing={2}>
              <Button
                component="label"
                variant="outlined"
                startIcon={<UploadFileIcon />}
                sx={{ alignSelf: "flex-start" }}
              >
                {file ? "Choose a different file" : "Choose resume file"}
                <input
                  hidden
                  type="file"
                  accept=".pdf,.docx"
                  onChange={(e) => pickFile(e.target.files?.[0])}
                />
              </Button>
              {file && (
                <Typography variant="body2" color="text.secondary">
                  Selected: <strong>{file.name}</strong> ({Math.round(file.size / 1024)} KB)
                </Typography>
              )}

              <TextField
                label="Name"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                size="small"
              />
              <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
                <TextField
                  label="Location"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  size="small"
                  fullWidth
                />
                <TextField
                  label="Grade"
                  value={grade}
                  onChange={(e) => setGrade(e.target.value)}
                  size="small"
                  fullWidth
                />
              </Stack>

              {error && <Alert severity="error">{error}</Alert>}

              <Box>
                <Button type="submit" variant="contained" disabled={loading || !file}>
                  {loading ? <CircularProgress size={22} color="inherit" /> : "Upload & extract"}
                </Button>
                {loading && (
                  <Typography variant="caption" color="text.secondary" sx={{ ml: 2 }}>
                    Extracting with Gemini — this can take up to a minute.
                  </Typography>
                )}
              </Box>
            </Stack>
          </form>
        </CardContent>
      </Card>

      {result && (
        <Card variant="outlined" sx={{ mt: 3, borderColor: "success.light" }}>
          <CardContent>
            <Alert severity="success" sx={{ mb: 2 }}>
              Added <strong>{result.name}</strong> to the talent pool.
            </Alert>
            <Typography variant="subtitle2" gutterBottom>
              Extracted from the resume
            </Typography>
            <Stack spacing={1.5} sx={{ mt: 1 }}>
              <Typography variant="body2">
                <strong>Experience:</strong> {result.experience_years} years
              </Typography>
              <Box>
                <Typography variant="body2" gutterBottom>
                  <strong>Skills</strong>
                </Typography>
                <Stack direction="row" flexWrap="wrap" gap={0.75}>
                  {result.skills?.map((s) => <Chip key={s} label={s} size="small" />)}
                </Stack>
              </Box>
              {result.certifications?.length > 0 && (
                <Box>
                  <Typography variant="body2" gutterBottom>
                    <strong>Certifications</strong>
                  </Typography>
                  <Stack direction="row" flexWrap="wrap" gap={0.75}>
                    {result.certifications.map((c) => (
                      <Chip key={c} label={c} size="small" variant="outlined" color="primary" />
                    ))}
                  </Stack>
                </Box>
              )}
              {result.domain_experience?.length > 0 && (
                <Box>
                  <Typography variant="body2" gutterBottom>
                    <strong>Domain experience</strong>
                  </Typography>
                  <Stack direction="row" flexWrap="wrap" gap={0.75}>
                    {result.domain_experience.map((d) => (
                      <Chip key={d} label={d} size="small" variant="outlined" />
                    ))}
                  </Stack>
                </Box>
              )}
              {result.previous_projects?.length > 0 && (
                <Box>
                  <Typography variant="body2" gutterBottom>
                    <strong>Projects</strong>
                  </Typography>
                  {result.previous_projects.map((p, i) => (
                    <Typography key={i} variant="body2" color="text.secondary">
                      • {p.name}
                      {p.description ? ` — ${p.description}` : ""}
                    </Typography>
                  ))}
                </Box>
              )}
            </Stack>
            <Divider sx={{ my: 2 }} />
            <Button variant="outlined" size="small" onClick={() => navigate(`/employee/${result.id}`)}>
              View full profile
            </Button>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}
