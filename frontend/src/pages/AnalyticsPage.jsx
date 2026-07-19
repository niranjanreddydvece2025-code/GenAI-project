import { Box, Card, CardContent, CircularProgress, Grid, Stack, Typography } from "@mui/material";
import React, { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import client from "../api/client.js";

const COLORS = ["#3F51B5", "#00A896", "#F5A623", "#E85D75", "#6C63FF", "#4CAF50"];

function StatCard({ label, value }) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="body2" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="h4" fontWeight={700}>
          {value}
        </Typography>
      </CardContent>
    </Card>
  );
}

export default function AnalyticsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.get("/analytics").then(({ data }) => setData(data)).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Stack alignItems="center" sx={{ py: 8 }}>
        <CircularProgress />
      </Stack>
    );
  }

  if (!data) return null;

  const skillData = Object.entries(data.skill_distribution).map(([skill, count]) => ({ skill, count }));
  const allocationPie = [
    { name: "Allocated", value: data.employees_allocated },
    { name: "On Bench", value: data.employees_on_bench },
  ];

  return (
    <Box>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        Resourcing Analytics
      </Typography>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} md={3}>
          <StatCard label="Total Employees" value={data.total_employees} />
        </Grid>
        <Grid item xs={6} md={3}>
          <StatCard label="On Bench" value={data.employees_on_bench} />
        </Grid>
        <Grid item xs={6} md={3}>
          <StatCard label="Allocated" value={data.employees_allocated} />
        </Grid>
        <Grid item xs={6} md={3}>
          <StatCard
            label="Avg. Allocation Time"
            value={data.average_allocation_time_days != null ? `${Math.round(data.average_allocation_time_days)}d` : "—"}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={7}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                Skill Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={skillData} layout="vertical" margin={{ left: 40 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" allowDecimals={false} />
                  <YAxis type="category" dataKey="skill" width={110} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3F51B5" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={5}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                Bench vs Allocated
              </Typography>
              <ResponsiveContainer width="100%" height={320}>
                <PieChart>
                  <Pie data={allocationPie} dataKey="value" nameKey="name" outerRadius={100} label>
                    {allocationPie.map((_, idx) => (
                      <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card variant="outlined">
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} gutterBottom>
                Most Requested Skills (from search queries)
              </Typography>
              {data.most_requested_skills.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No shortlist activity yet.
                </Typography>
              ) : (
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={data.most_requested_skills}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="skill" tick={{ fontSize: 12 }} />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#00A896" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
