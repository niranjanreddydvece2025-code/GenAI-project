import LogoutIcon from "@mui/icons-material/Logout";
import { AppBar, Box, Button, Container, IconButton, Tab, Tabs, Toolbar, Typography } from "@mui/material";
import React from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

const TABS = [
  { label: "Chatbot Search", path: "/" },
  { label: "Shortlist", path: "/shortlist" },
  { label: "Analytics", path: "/analytics" },
];

// Uploading employee profiles is a Resource Manager responsibility.
const RESOURCE_MANAGER_TABS = [{ label: "Upload Resume", path: "/upload" }];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const tabs =
    user?.role === "resource_manager" ? [...TABS, ...RESOURCE_MANAGER_TABS] : TABS;
  const currentTab = tabs.some((t) => t.path === location.pathname) ? location.pathname : false;

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "background.default" }}>
      <AppBar position="static" elevation={0} color="primary">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 0, mr: 4, fontWeight: 700 }}>
            GenAI Resource Allocation
          </Typography>
          <Tabs
            value={currentTab}
            onChange={(_, value) => navigate(value)}
            textColor="inherit"
            indicatorColor="secondary"
            sx={{ flexGrow: 1 }}
          >
            {tabs.map((t) => (
              <Tab key={t.path} label={t.label} value={t.path} />
            ))}
          </Tabs>
          <Typography variant="body2" sx={{ mr: 2, opacity: 0.85 }}>
            {user?.email} ({user?.role === "resource_manager" ? "Resource Manager" : "Project Manager"})
          </Typography>
          <IconButton color="inherit" onClick={() => { logout(); navigate("/login"); }}>
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Outlet />
      </Container>
    </Box>
  );
}
