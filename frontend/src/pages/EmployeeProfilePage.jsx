import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { Box, Button, Card, CardContent, Chip, CircularProgress, Divider, Grid, Stack, Typography } from "@mui/material";
import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import client from "../api/client.js";

function Section({ title, children }) {
  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="subtitle1" fontWeight={700} gutterBottom>
        {title}
      </Typography>
      {children}
    </Box>
  );
}

export default function EmployeeProfilePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [employee, setEmployee] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client
      .get(`/employee/${id}`)
      .then(({ data }) => setEmployee(data))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <Stack alignItems="center" sx={{ py: 8 }}>
        <CircularProgress />
      </Stack>
    );
  }

  if (!employee) {
    return <Typography>Employee not found.</Typography>;
  }

  return (
    <Box>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate(-1)} sx={{ mb: 2 }}>
        Back
      </Button>
      <Card variant="outlined">
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h4" fontWeight={700}>
            {employee.name}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
            {employee.grade} · {employee.location} · {employee.experience_years} years experience
          </Typography>
          <Chip
            label={`Rating: ${employee.performance_rating}/5`}
            color="secondary"
            size="small"
            sx={{ mb: 3 }}
          />

          <Divider sx={{ mb: 3 }} />

          <Section title="AI Summary">
            <Typography variant="body2">{employee.ai_summary || "No summary generated yet."}</Typography>
          </Section>

          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <Section title="Skills">
                <Stack direction="row" spacing={1} sx={{ flexWrap: "wrap", gap: 1 }}>
                  {(employee.skills || []).map((s) => (
                    <Chip key={s} label={s} size="small" />
                  ))}
                </Stack>
              </Section>

              <Section title="Domain Experience">
                <Stack direction="row" spacing={1} sx={{ flexWrap: "wrap", gap: 1 }}>
                  {(employee.domain_experience || []).map((d) => (
                    <Chip key={d} label={d} size="small" color="primary" variant="outlined" />
                  ))}
                </Stack>
              </Section>

              <Section title="Certifications">
                <Stack direction="row" spacing={1} sx={{ flexWrap: "wrap", gap: 1 }}>
                  {(employee.certifications || []).length === 0 && (
                    <Typography variant="body2" color="text.secondary">None on file</Typography>
                  )}
                  {(employee.certifications || []).map((c) => (
                    <Chip key={c} label={c} size="small" color="success" variant="outlined" />
                  ))}
                </Stack>
              </Section>
            </Grid>

            <Grid item xs={12} md={6}>
              <Section title="Availability">
                <Typography variant="body2">
                  {employee.availability_date === new Date().toISOString().slice(0, 10)
                    ? "Available immediately"
                    : `Available from ${employee.availability_date}`}
                </Typography>
              </Section>

              <Section title="Current Allocation">
                <Typography variant="body2">{employee.current_allocation || "On bench"}</Typography>
              </Section>

              <Section title="Previous Projects">
                <Stack spacing={1}>
                  {(employee.previous_projects || []).length === 0 && (
                    <Typography variant="body2" color="text.secondary">No projects on file</Typography>
                  )}
                  {(employee.previous_projects || []).map((p, idx) => (
                    <Card key={idx} variant="outlined" sx={{ p: 1.5 }}>
                      <Typography variant="body2" fontWeight={600}>
                        {p.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {p.description}
                      </Typography>
                    </Card>
                  ))}
                </Stack>
              </Section>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
}
