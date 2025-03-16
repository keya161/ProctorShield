
"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import {
  ShieldAlert,
  Activity,
  Bell,
  Settings,
  FileDown,
  MousePointerClick,
  GlobeLock,
  UserCircle,
  Layers,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/lib/utils";

const tabs = [
  { id: "dashboard", label: "System Overview", icon: Activity },
  { id: "alerts", label: "Security Alerts", icon: Bell },
  { id: "settings", label: "Configurations", icon: Settings },
];

// Sample candidate data with tab switch offenses and cheat detection statuses
const candidates = [
  {
    id: 1,
    name: "Candidate 1",
    tabSwitches: 3,
    peripherals: "Unusual Activity",
    browserAuth: "Failed",
  },
  {
    id: 2,
    name: "Candidate 2",
    tabSwitches: 0,
    peripherals: "Normal",
    browserAuth: "Passed",
  },
  {
    id: 3,
    name: "Candidate 3",
    tabSwitches: 5,
    peripherals: "Normal",
    browserAuth: "Failed",
  },
  {
    id: 4,
    name: "Candidate 4",
    tabSwitches: 1,
    peripherals: "Unusual Activity",
    browserAuth: "Passed",
  },
];

export default function SecurityDashboard() {
  const [activeTab, setActiveTab] = useState("dashboard");

  const handleDownloadReport = (candidateId: number) => {
    // Simulate a download process (Replace with actual report generation logic)
    alert(`Downloading report for Candidate ${candidateId}`);
  };

  const renderDashboardContent = () => (
    <div className="grid gap-6">
      {/* System Overview */}
      <div className="grid gap-6 md:grid-cols-3">
        <Card className="p-6 bg-blue-900 text-white">
          <div className="flex items-center gap-4">
            <Activity className="h-8 w-8 text-yellow-300" />
            <div>
              <h3 className="text-sm font-medium">Active Candidates</h3>
              <p className="text-2xl font-bold">{candidates.length}</p>
            </div>
          </div>
        </Card>
        <Card className="p-6 bg-red-800 text-white">
          <div className="flex items-center gap-4">
            <ShieldAlert className="h-8 w-8 text-white" />
            <div>
              <h3 className="text-sm font-medium">Security Alerts</h3>
              <p className="text-2xl font-bold">7</p>
            </div>
          </div>
        </Card>
        <Card className="p-6 bg-green-700 text-white">
          <div className="flex items-center gap-4">
            <Activity className="h-8 w-8 text-white" />
            <div>
              <h3 className="text-sm font-medium">System Stability</h3>
              <p className="text-2xl font-bold">Operational</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Candidate Monitoring Panel */}
      <Card className="p-6 bg-gray-800 text-white">
        <h2 className="text-xl font-semibold mb-4">Candidate Monitoring</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
          {candidates.map((candidate) => (
            <Card key={candidate.id} className="p-4 bg-gray-900 text-white">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-4">
                  <UserCircle className="h-10 w-10 text-blue-400" />
                  <h3 className="text-lg font-semibold">{candidate.name}</h3>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="border-white text-white"
                  onClick={() => handleDownloadReport(candidate.id)}
                >
                  <FileDown className="h-4 w-4 mr-2" />
                  Download Report
                </Button>
              </div>

              {/* Cheat Detection Flags */}
              <div className="grid grid-cols-3 gap-4">
                {/* Tab Switches */}
                <Card
                  className={cn(
                    "p-3 text-white text-sm",
                    candidate.tabSwitches === 0
                      ? "bg-blue-700"
                      : candidate.tabSwitches <= 2
                      ? "bg-yellow-600"
                      : "bg-red-700"
                  )}
                >
                  <div className="flex items-center gap-2">
                    <Layers className="h-5 w-5 text-white" />
                    <p>Tab Switches</p>
                  </div>
                  <p className="font-bold mt-1">{candidate.tabSwitches} Offenses</p>
                </Card>

                {/* Peripheral Devices */}
                <Card
                  className={cn(
                    "p-3 text-white text-sm",
                    candidate.peripherals === "Normal"
                      ? "bg-blue-700"
                      : "bg-yellow-600"
                  )}
                >
                  <div className="flex items-center gap-2">
                    <MousePointerClick className="h-5 w-5 text-white" />
                    <p>Peripherals</p>
                  </div>
                  <p className="font-bold mt-1">{candidate.peripherals}</p>
                </Card>

                {/* Browser Authentication */}
                <Card
                  className={cn(
                    "p-3 text-white text-sm",
                    candidate.browserAuth === "Passed" ? "bg-blue-700" : "bg-red-700"
                  )}
                >
                  <div className="flex items-center gap-2">
                    <GlobeLock className="h-5 w-5 text-white" />
                    <p>Browser Auth</p>
                  </div>
                  <p className="font-bold mt-1">{candidate.browserAuth}</p>
                </Card>
              </div>
            </Card>
          ))}
        </div>
      </Card>
    </div>
  );

  const renderAlertsContent = () => (
    <Card className="p-6 bg-yellow-800 text-white">
      <h2 className="text-xl font-semibold mb-4">Recent Security Alerts</h2>
      <div className="space-y-4">
        {[1, 2, 3].map((_, i) => (
          <div key={i} className="flex items-center gap-4 p-4 rounded-lg bg-yellow-600">
            <div className="w-2 h-2 rounded-full bg-red-500" />
            <div className="flex-1">
              <h4 className="font-medium">Unauthorized Access Attempt</h4>
              <p className="text-sm">Candidate {i + 2}</p>
            </div>
            <Button variant="outline" size="sm" className="border-white text-white">
              Investigate
            </Button>
          </div>
        ))}
      </div>
    </Card>
  );

  const renderSettingsContent = () => (
    <Card className="p-6 bg-gray-700 text-white">
      <h2 className="text-xl font-semibold mb-4">System Configurations</h2>
      <p className="text-gray-400">Modify security preferences and adjust monitoring thresholds here.</p>
    </Card>
  );

  const renderContent = () => {
    switch (activeTab) {
      case "dashboard":
        return renderDashboardContent();
      case "alerts":
        return renderAlertsContent();
      case "settings":
        return renderSettingsContent();
      default:
        return renderDashboardContent();
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      <div className="w-64 border-r bg-gray-900 text-white">
        <nav className="space-y-2 p-4">
          {tabs.map(({ id, label, icon: Icon }) => (
            <button key={id} onClick={() => setActiveTab(id)} className={cn("flex items-center gap-3 w-full rounded-lg px-3 py-2", activeTab === id ? "bg-blue-700 text-white" : "hover:bg-gray-700")}>
              <Icon className="h-4 w-4" />
              {label}
            </button>
          ))}
        </nav>
      </div>
      <div className="flex-1 overflow-auto p-6 bg-gray-800">{renderContent()}</div>
    </div>
  );
}