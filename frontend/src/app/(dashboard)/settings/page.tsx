"use client";

import React, { useState } from "react";
import { Card, CardContent, CardHeader } from "@/components/Card";
import Input from "@/components/Input";
import Button from "@/components/Button";
import Badge from "@/components/Badge";
import { getUser } from "@/lib/auth";

export default function SettingsPage() {
  const user = getUser();
  const [activeTab, setActiveTab] = useState<"account" | "security" | "billing" | "api">("account");
  const [formData, setFormData] = useState({
    full_name: user?.full_name || "",
    email: user?.email || "",
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
        <p className="text-gray-400">Manage your account and preferences</p>
      </div>

      {/* Tabs */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-2 border-b border-gray-800">
            {[
              { id: "account", label: "Account" },
              { id: "security", label: "Security" },
              { id: "billing", label: "Billing" },
              { id: "api", label: "API" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 py-3 font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? "text-red-600 border-red-600"
                    : "text-gray-400 border-transparent hover:text-gray-300"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Account Settings */}
      {activeTab === "account" && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-white">Account Settings</h3>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              label="Full Name"
              value={formData.full_name}
              onChange={(e) =>
                setFormData({ ...formData, full_name: e.target.value })
              }
            />
            <Input
              label="Email Address"
              type="email"
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
            />
            <div>
              <label className="block text-sm font-medium text-gray-200 mb-2">
                Role
              </label>
              <div className="p-3 bg-gray-800/30 rounded-lg border border-gray-700">
                <Badge variant="info">{user?.role}</Badge>
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="primary">Save Changes</Button>
              <Button variant="outline">Cancel</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Security Settings */}
      {activeTab === "security" && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-white">Password</h3>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input label="Current Password" type="password" />
              <Input label="New Password" type="password" />
              <Input label="Confirm Password" type="password" />
              <Button variant="primary">Update Password</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-white">
                Two-Factor Authentication
              </h3>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 bg-yellow-900/20 border border-yellow-800/30 rounded-lg">
                <p className="text-sm text-yellow-300">
                  2FA is not enabled. Enable it to add an extra layer of security to your account.
                </p>
              </div>
              <Button variant="secondary">Enable 2FA</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-white">
                Active Sessions
              </h3>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="p-3 bg-gray-800/30 rounded-lg border border-gray-700">
                <p className="text-sm text-gray-300 mb-1">Current Session</p>
                <p className="text-xs text-gray-400">Chrome • 127.0.0.1</p>
              </div>
              <Button variant="danger" size="sm">
                Sign Out All Sessions
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Billing Settings */}
      {activeTab === "billing" && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-white">Billing</h3>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 bg-blue-900/20 border border-blue-800/30 rounded-lg">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="text-white font-medium">Pro Plan</p>
                  <p className="text-sm text-blue-300">Active During Beta</p>
                </div>
                <Badge variant="success">Active</Badge>
              </div>
              <p className="text-sm text-blue-300">
                You have unlimited access to all features during the beta phase. No billing required.
              </p>
            </div>

            <div className="p-4 bg-gray-800/30 border border-gray-700 rounded-lg">
              <p className="text-sm text-gray-300 mb-2">Plan Benefits:</p>
              <ul className="text-sm text-gray-400 space-y-1">
                <li>• Unlimited scans</li>
                <li>• All 456 attack techniques</li>
                <li>• 6 compliance frameworks</li>
                <li>• Real-time monitoring</li>
                <li>• Priority support</li>
                <li>• Custom integrations</li>
              </ul>
            </div>

            <Button variant="outline">Upgrade After Beta</Button>
          </CardContent>
        </Card>
      )}

      {/* API Settings */}
      {activeTab === "api" && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold text-white">API Keys</h3>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 bg-gray-800/30 rounded-lg border border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <p className="text-white font-medium">Personal API Key</p>
                <Button variant="ghost" size="sm">
                  Copy
                </Button>
              </div>
              <code className="text-xs text-gray-400 break-all">
                ar_live_abc123def456ghi789jkl012mno345
              </code>
            </div>
            <p className="text-sm text-gray-400">
              Use this key to authenticate API requests. Keep it secret and never share it.
            </p>
            <Button variant="danger" size="sm">
              Regenerate Key
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
