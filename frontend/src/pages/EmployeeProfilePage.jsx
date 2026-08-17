import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  Grid,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import client from "../api/client.js";

// Compares against the viewer's local date, not UTC. Using toISOString() here would
// report someone free today as "available from <today>" for anyone east of UTC
// during their early-morning hours. A past date still counts as available now.
function isAvailableNow(availabilityDate) {
  if (!availabilityDate) return false;
  const today = new Date();
  const localToday = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(
    today.getDate(),
  ).padStart(2, "0")}`;
  return availabilityDate <= localToday;
}

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
  const [openAllocationDialog, setOpenAllocationDialog] = useState(false);
  const [projects, setProjects] = useState([]);
  const [projectsLoading, setProjectsLoading] = useState(false);
  const [allocationForm, setAllocationForm] = useState({
    project_id: "",
    allocation_date: new Date().toISOString().split("T")[0],
  });
  const [submitting, setSubmitting] = useState(false);
  const [allocationError, setAllocationError] = useState("");

  useEffect(() => {
    client
      .get(`/employee/${id}`)
      .then(({ data }) => setEmployee(data))
      .finally(() => setLoading(false));
  }, [id]);

  const handleOpenAllocationDialog = async () => {
    setProjectsLoading(true);
    setAllocationError("");
    try {
      const { data } = await client.get("/allocations/projects");
      setProjects(data);
    } catch (err) {
      setAllocationError("Failed to load projects");
      console.error(err);
    } finally {
      setProjectsLoading(false);
    }
    setOpenAllocationDialog(true);
  };

  const handleCloseAllocationDialog = () => {
    setOpenAllocationDialog(false);
    setAllocationForm({
      project_id: "",
      allocation_date: new Date().toISOString().split("T")[0],
    });
    setAllocationError("");
  };

  const handleAllocationSubmit = async () => {
    if (!allocationForm.project_id || !allocationForm.allocation_date) {
      setAllocationError("Please fill in all fields");
      return;
    }

    setSubmitting(true);
    setAllocationError("");
    try {
      await client.post("/allocations", {
        employee_id: parseInt(id),
        project_id: parseInt(allocationForm.project_id),
        allocation_date: allocationForm.allocation_date,
      });
      handleCloseAllocationDialog();
      // Optionally refresh employee data
      const { data } = await client.get(`/employee/${id}`);
      setEmployee(data);
    } catch (err) {
      setAllocationError(err.response?.data?.detail || "Failed to create allocation");
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

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
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 3 }}>
            <Box>
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
            </Box>
            <Button
              variant="contained"
              size="small"
              onClick={handleOpenAllocationDialog}
              sx={{ mt: 1 }}
            >
              Allocate
            </Button>
          </Stack>

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
                  {isAvailableNow(employee.availability_date)
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

      {/* Allocation Dialog */}
      <Dialog open={openAllocationDialog} onClose={handleCloseAllocationDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Allocate Employee to Project</DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          {allocationError && (
            <Typography variant="body2" color="error" sx={{ mb: 2 }}>
              {allocationError}
            </Typography>
          )}
          <TextField
            select
            label="Project"
            fullWidth
            value={allocationForm.project_id}
            onChange={(e) => setAllocationForm({ ...allocationForm, project_id: e.target.value })}
            disabled={projectsLoading || submitting}
            sx={{ mb: 2 }}
          >
            <MenuItem value="">-- Select a project --</MenuItem>
            {projects.map((project) => (
              <MenuItem key={project.id} value={project.id}>
                {project.name} {project.location ? `(${project.location})` : ""}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            type="date"
            label="Allocation Date"
            fullWidth
            value={allocationForm.allocation_date}
            onChange={(e) => setAllocationForm({ ...allocationForm, allocation_date: e.target.value })}
            InputLabelProps={{ shrink: true }}
            disabled={submitting}
          />
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={handleCloseAllocationDialog} disabled={submitting}>
            Cancel
          </Button>
          <Button
            onClick={handleAllocationSubmit}
            variant="contained"
            disabled={projectsLoading || submitting}
          >
            {submitting ? "Allocating..." : "Allocate"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
