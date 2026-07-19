import SendIcon from "@mui/icons-material/Send";
import { Alert, Box, Button, CircularProgress, Paper, Stack, TextField, Typography } from "@mui/material";
import React, { useState } from "react";
import client from "../api/client.js";
import CandidateCard from "../components/CandidateCard.jsx";
import { useAuth } from "../context/AuthContext.jsx";

const EXAMPLES = [
  "Find two Oracle EBS developers with SQL, Finance domain experience, and immediate availability.",
  "I need three Java developers with AWS experience in Bangalore.",
  "Find a DevOps engineer with Kubernetes and Terraform experience.",
];

export default function ChatbotPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [shortlistedIds, setShortlistedIds] = useState(new Set());
  const { user } = useAuth();

  const runSearch = async (q) => {
    const searchQuery = q ?? query;
    if (!searchQuery.trim()) return;
    setLoading(true);
    setError("");
    setResults(null);
    try {
      const { data } = await client.post("/searchCandidates", { query: searchQuery, top_k: 5 });
      setResults(data);
    } catch (err) {
      setError(err?.response?.data?.detail || "Search failed. Check backend logs / Gemini API key.");
    } finally {
      setLoading(false);
    }
  };

  const handleShortlist = async (candidate) => {
    try {
      await client.post("/shortlist", {
        employee_id: candidate.employee.id,
        manager_email: user?.email || "unknown@example.com",
        query_text: results?.query,
        match_score: candidate.match_percent,
      });
      setShortlistedIds((prev) => new Set(prev).add(candidate.employee.id));
    } catch (err) {
      setError("Could not shortlist candidate.");
    }
  };

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        Find the right people, in natural language
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Describe the role you need staffed. Skills, domain, location, availability — the assistant understands it all.
      </Typography>

      <Paper elevation={0} variant="outlined" sx={{ p: 2, mb: 2 }}>
        <Stack direction="row" spacing={1}>
          <TextField
            fullWidth
            placeholder='e.g. "Find two Oracle EBS developers with SQL, Finance domain experience, and immediate availability."'
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && runSearch()}
          />
          <Button
            variant="contained"
            endIcon={<SendIcon />}
            onClick={() => runSearch()}
            disabled={loading}
            sx={{ px: 3 }}
          >
            Search
          </Button>
        </Stack>
        <Stack direction="row" spacing={1} sx={{ mt: 1.5, flexWrap: "wrap", gap: 1 }}>
          {EXAMPLES.map((ex) => (
            <Button key={ex} size="small" variant="text" onClick={() => { setQuery(ex); runSearch(ex); }}>
              {ex.length > 55 ? ex.slice(0, 55) + "…" : ex}
            </Button>
          ))}
        </Stack>
      </Paper>

      {loading && (
        <Stack alignItems="center" sx={{ py: 6 }}>
          <CircularProgress />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Understanding your request and ranking candidates...
          </Typography>
        </Stack>
      )}

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {results && !loading && (
        <Box>
          <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1 }}>
            {results.candidates.length} recommended candidate{results.candidates.length !== 1 ? "s" : ""}
          </Typography>
          {results.candidates.length === 0 && (
            <Alert severity="info">No matching candidates found. Try broadening the query.</Alert>
          )}
          {results.candidates.map((c) => (
            <CandidateCard
              key={c.employee.id}
              candidate={c}
              onShortlist={handleShortlist}
              isShortlisted={shortlistedIds.has(c.employee.id)}
            />
          ))}
        </Box>
      )}
    </Box>
  );
}
