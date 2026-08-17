import SearchIcon from "@mui/icons-material/Search";
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import React, { useEffect, useState } from "react";
import client from "../api/client.js";
import CandidateCard from "../components/CandidateCard.jsx";
import { useAuth } from "../context/AuthContext.jsx";

export default function LocationSearchPage() {
  const [locations, setLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [locationLoading, setLocationLoading] = useState(true);
  const [error, setError] = useState("");
  const [shortlistedIds, setShortlistedIds] = useState(new Set());
  const [skillFilter, setSkillFilter] = useState("");
  const [availabilityFilter, setAvailabilityFilter] = useState(false);
  const [searched, setSearched] = useState(false);
  const { user } = useAuth();

  const buildSearchQuery = (location, skill = "", availability = false) => {
    const parts = [];
    const skills = (skill || "")
      .split(/[\n,;]+/)
      .map((item) => item.trim())
      .filter(Boolean);

    if (skills.length > 0) {
      parts.push(`skills: ${skills.join(", ")}`);
    }

    if (location) {
      parts.push(`location: ${location}`);
    }

    if (availability) {
      parts.push("immediate availability");
    }

    return parts.join("; ");
  };

  const filterCandidates = async (location, skill = "", availability = false) => {
    setLoading(true);
    setError("");

    try {
      const query = buildSearchQuery(location, skill, availability);
      if (!query.trim()) {
        setCandidates([]);
        return;
      }

      const { data } = await client.post("/searchCandidates", {
        query,
        top_k: 50,
      });

      setCandidates(data?.candidates ?? []);
    } catch (err) {
      console.error("Error searching candidates:", err);
      setError(err?.response?.data?.detail || "Failed to load candidates.");
    } finally {
      setLoading(false);
    }
  };

  // Fetch all unique locations when component mounts
  useEffect(() => {
    async function fetchLocations() {
      try {
        const { data } = await client.get("/employees");
        const uniqueLocations = [...new Set(data.map((emp) => emp.location).filter(Boolean))].sort();
        setLocations(uniqueLocations);
      } catch (err) {
        setError("Failed to load locations.");
      } finally {
        setLocationLoading(false);
      }
    }
    fetchLocations();
  }, []);

  // Reapply filters when skill or availability filter changes (only if already searched)
  useEffect(() => {
    if (searched) {
      filterCandidates(selectedLocation, skillFilter, availabilityFilter);
    }
  }, [skillFilter, availabilityFilter]);

  // Search candidates when location is selected
  const handleLocationChange = async (event, newValue) => {
    setSelectedLocation(newValue);
    setSearched(false);
    setCandidates([]);
  };

  // Handle search button click
  const handleSearch = async () => {
    setSearched(true);
    await filterCandidates(selectedLocation, skillFilter, availabilityFilter);
  };

  const handleShortlist = async (candidateData) => {
    try {
      await client.post("/shortlist", {
        employee_id: candidateData.employee.id,
        manager_email: user?.email || "unknown@example.com",
        query_text: `Location: ${selectedLocation}`,
        match_score: candidateData.match_percent,
      });
      setShortlistedIds((prev) => new Set(prev).add(candidateData.employee.id));
    } catch (err) {
      setError("Could not shortlist candidate.");
    }
  };

  if (locationLoading) {
    return (
      <Stack alignItems="center" sx={{ py: 8 }}>
        <CircularProgress />
      </Stack>
    );
  }

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        Search Candidates
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Find candidates by location (optional) with skill and availability filters.
      </Typography>

      {/* Location Selection */}
      <Card elevation={0} variant="outlined" sx={{ p: 2, mb: 3 }}>
        <Stack spacing={2}>
          <Autocomplete
            options={locations}
            value={selectedLocation}
            onChange={handleLocationChange}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Select Location"
                placeholder="Type or select a location..."
                slotProps={{
                  input: {
                    ...params.InputProps,
                    startAdornment: (
                      <>
                        <SearchIcon sx={{ mr: 1, color: "text.secondary" }} />
                        {params.InputProps.startAdornment}
                      </>
                    ),
                  },
                }}
              />
            )}
            freeSolo
            fullWidth
          />

          {/* Additional Filters */}
          {selectedLocation && (
            <Stack spacing={2} sx={{ pt: 1, borderTop: "1px solid", borderColor: "divider" }}>
              <Typography variant="subtitle2" fontWeight={600}>
                Additional Filters
              </Typography>

              <TextField
                size="small"
                label="Filter by Skill (optional)"
                placeholder="e.g., Java, Python, AWS"
                value={skillFilter}
                onChange={(e) => setSkillFilter(e.target.value)}
              />

              <Stack direction="row" spacing={1} alignItems="center">
                <Chip
                  label="Immediately Available"
                  onClick={() => setAvailabilityFilter(!availabilityFilter)}
                  color={availabilityFilter ? "primary" : "default"}
                  variant={availabilityFilter ? "filled" : "outlined"}
                  sx={{ cursor: "pointer" }}
                />
              </Stack>

              {/* Apply Filters Button & Results Count */}
              <Stack direction="row" spacing={1}>
                <Box 
                  sx={{ 
                    flex: 1,
                    p: 1, 
                    bgcolor: "background.paper",
                    border: "1px solid",
                    borderColor: "divider",
                    borderRadius: 1,
                    textAlign: "center"
                  }}
                >
                  <Typography variant="body2" fontWeight={600}>
                    {searched ? `${candidates.length} candidate(s) found` : "Click Search to view candidates"}
                  </Typography>
                </Box>
              </Stack>

              {/* Search Button */}
              <Button
                variant="contained"
                size="large"
                onClick={handleSearch}
                disabled={loading}
                sx={{ mt: 2 }}
              >
                Search
              </Button>
            </Stack>
          )}

          {/* General Filters (when no location selected) */}
          {!selectedLocation && (
            <Stack spacing={2} sx={{ pt: 1, borderTop: "1px solid", borderColor: "divider" }}>
              <Typography variant="subtitle2" fontWeight={600}>
                Filters
              </Typography>

              <TextField
                size="small"
                label="Filter by Skill (optional)"
                placeholder="e.g., Java, Python, AWS"
                value={skillFilter}
                onChange={(e) => setSkillFilter(e.target.value)}
              />

              <Stack direction="row" spacing={1} alignItems="center">
                <Chip
                  label="Immediately Available"
                  onClick={() => setAvailabilityFilter(!availabilityFilter)}
                  color={availabilityFilter ? "primary" : "default"}
                  variant={availabilityFilter ? "filled" : "outlined"}
                  sx={{ cursor: "pointer" }}
                />
              </Stack>

              {/* Results Count */}
              <Stack direction="row" spacing={1}>
                <Box 
                  sx={{ 
                    flex: 1,
                    p: 1, 
                    bgcolor: "background.paper",
                    border: "1px solid",
                    borderColor: "divider",
                    borderRadius: 1,
                    textAlign: "center"
                  }}
                >
                  <Typography variant="body2" fontWeight={600}>
                    {searched ? `${candidates.length} candidate(s) found` : "Click Search to view candidates"}
                  </Typography>
                </Box>
              </Stack>

              {/* Search Button */}
              <Button
                variant="contained"
                size="large"
                onClick={handleSearch}
                disabled={loading}
                sx={{ mt: 2 }}
              >
                Search
              </Button>
            </Stack>
          )}
        </Stack>
      </Card>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Loading State */}
      {loading && (
        <Stack alignItems="center" sx={{ py: 6 }}>
          <CircularProgress />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Loading candidates...
          </Typography>
        </Stack>
      )}

      {/* Results */}
      {!loading && searched && (
        <>
          {candidates.length === 0 && (
            <Alert severity="info">
              No candidates found{selectedLocation ? ` for ${selectedLocation}` : ""}
              {skillFilter && ` with "${skillFilter}" skills`}
              {availabilityFilter && " who are immediately available"}. Try adjusting your filters.
            </Alert>
          )}

          <Stack spacing={2}>
            {candidates.map((candidate) => (
              <CandidateCard
                key={candidate.employee.id}
                candidate={candidate}
                isShortlisted={shortlistedIds.has(candidate.employee.id)}
                onShortlist={() => handleShortlist(candidate)}
              />
            ))}
          </Stack>
        </>
      )}

      {/* No Search Yet Message */}
      {!loading && !searched && (
        <Typography variant="body2" color="text.secondary" sx={{ textAlign: "center", py: 8 }}>
          Set your filters and click "Search" to view candidates
        </Typography>
      )}
    </Box>
  );
}
