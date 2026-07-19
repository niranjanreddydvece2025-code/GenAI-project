import BookmarkAddIcon from "@mui/icons-material/BookmarkAdd";
import BookmarkAddedIcon from "@mui/icons-material/BookmarkAdded";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Stack,
  Typography,
} from "@mui/material";
import React from "react";
import { useNavigate } from "react-router-dom";

function matchColor(pct) {
  if (pct >= 85) return "success";
  if (pct >= 65) return "warning";
  return "error";
}

export default function CandidateCard({ candidate, onShortlist, isShortlisted }) {
  const navigate = useNavigate();
  const { employee, match_percent: matchPercent, reasons, ai_summary: aiSummary } = candidate;

  return (
    <Card variant="outlined" sx={{ mb: 2 }}>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography variant="h6" fontWeight={700}>
              {employee.name}{" "}
              <Chip
                size="small"
                color={matchColor(matchPercent)}
                label={`${matchPercent}% match`}
                sx={{ ml: 1, fontWeight: 600 }}
              />
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {employee.grade} · {employee.location} · {employee.experience_years} yrs experience
            </Typography>
          </Box>
          <Stack direction="row" spacing={1}>
            <Button size="small" variant="outlined" onClick={() => navigate(`/employee/${employee.id}`)}>
              View Profile
            </Button>
            <Button
              size="small"
              variant={isShortlisted ? "contained" : "outlined"}
              color="secondary"
              startIcon={isShortlisted ? <BookmarkAddedIcon /> : <BookmarkAddIcon />}
              onClick={() => onShortlist(candidate)}
              disabled={isShortlisted}
            >
              {isShortlisted ? "Shortlisted" : "Shortlist"}
            </Button>
          </Stack>
        </Stack>

        <LinearProgress
          variant="determinate"
          value={matchPercent}
          color={matchColor(matchPercent)}
          sx={{ my: 1.5, height: 8, borderRadius: 4 }}
        />

        <Stack direction="row" spacing={1} sx={{ flexWrap: "wrap", gap: 1, mb: 1.5 }}>
          {(employee.skills || []).slice(0, 8).map((skill) => (
            <Chip key={skill} label={skill} size="small" variant="outlined" />
          ))}
        </Stack>

        <Typography variant="body2" sx={{ mb: 1 }}>
          {aiSummary}
        </Typography>

        <Typography variant="caption" color="text.secondary" fontWeight={600}>
          Recommended because:
        </Typography>
        <Stack direction="row" spacing={1} sx={{ flexWrap: "wrap", gap: 0.5, mt: 0.5 }}>
          {reasons.map((r) => (
            <Chip key={r} label={r} size="small" color="secondary" variant="outlined" />
          ))}
        </Stack>
      </CardContent>
    </Card>
  );
}
