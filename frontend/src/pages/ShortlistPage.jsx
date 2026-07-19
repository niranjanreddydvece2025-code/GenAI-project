import { Box, Button, Card, CardContent, Chip, CircularProgress, Stack, Typography } from "@mui/material";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client.js";
import { useAuth } from "../context/AuthContext.jsx";

export default function ShortlistPage() {
  const [entries, setEntries] = useState([]);
  const [employees, setEmployees] = useState({});
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    async function load() {
      const { data: shortlist } = await client.get("/shortlist", { params: { manager_email: user?.email } });
      setEntries(shortlist);
      const { data: allEmployees } = await client.get("/employees");
      const map = {};
      allEmployees.forEach((e) => (map[e.id] = e));
      setEmployees(map);
      setLoading(false);
    }
    load();
  }, [user]);

  if (loading) {
    return (
      <Stack alignItems="center" sx={{ py: 8 }}>
        <CircularProgress />
      </Stack>
    );
  }

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        My Shortlist
      </Typography>
      {entries.length === 0 && (
        <Typography variant="body2" color="text.secondary">
          You haven't shortlisted anyone yet. Go to Chatbot Search to find candidates.
        </Typography>
      )}
      <Stack spacing={2}>
        {entries.map((entry) => {
          const emp = employees[entry.employee_id];
          return (
            <Card key={entry.id} variant="outlined">
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography variant="subtitle1" fontWeight={700}>
                      {emp?.name || `Employee #${entry.employee_id}`}
                      {entry.match_score != null && (
                        <Chip size="small" label={`${entry.match_score}% match`} color="success" sx={{ ml: 1 }} />
                      )}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      From query: "{entry.query_text}"
                    </Typography>
                  </Box>
                  <Button variant="outlined" size="small" onClick={() => navigate(`/employee/${entry.employee_id}`)}>
                    View Profile
                  </Button>
                </Stack>
              </CardContent>
            </Card>
          );
        })}
      </Stack>
    </Box>
  );
}
