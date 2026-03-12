"use client";

import React, { useState } from "react";
import { Card, CardContent, CardHeader } from "@/components/Card";
import Badge from "@/components/Badge";
import Button from "@/components/Button";
import Input from "@/components/Input";
import { formatDate } from "@/lib/utils";

interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: "Owner" | "Admin" | "Member" | "Viewer";
  lastActive: string;
  twoFaEnabled: boolean;
  avatar?: string;
}

interface PendingInvite {
  id: string;
  email: string;
  role: "Owner" | "Admin" | "Member" | "Viewer";
  sentAt: string;
}

export default function TeamPage() {
  const [mounted, setMounted] = useState(false);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteFormData, setInviteFormData] = useState({
    email: "",
    role: "Member" as const,
  });

  // Mock team members
  const [members, setMembers] = useState<TeamMember[]>([
    {
      id: "user_1",
      name: "Sarah Johnson",
      email: "sarah@securitylabs.com",
      role: "Owner",
      lastActive: new Date(Date.now() - 5 * 60000).toISOString(),
      twoFaEnabled: true,
      avatar: "👩",
    },
    {
      id: "user_2",
      name: "Mike Chen",
      email: "mike@securitylabs.com",
      role: "Admin",
      lastActive: new Date(Date.now() - 30 * 60000).toISOString(),
      twoFaEnabled: true,
      avatar: "👨",
    },
    {
      id: "user_3",
      name: "Alice Rodriguez",
      email: "alice@securitylabs.com",
      role: "Member",
      lastActive: new Date(Date.now() - 2 * 3600000).toISOString(),
      twoFaEnabled: false,
      avatar: "👩",
    },
    {
      id: "user_4",
      name: "Bob Wilson",
      email: "bob@securitylabs.com",
      role: "Member",
      lastActive: new Date(Date.now() - 24 * 3600000).toISOString(),
      twoFaEnabled: true,
      avatar: "👨",
    },
  ]);

  // Mock pending invites
  const [pendingInvites, setPendingInvites] = useState<PendingInvite[]>([
    {
      id: "inv_1",
      email: "david@securitylabs.com",
      role: "Member",
      sentAt: new Date(Date.now() - 7 * 24 * 3600000).toISOString(),
    },
    {
      id: "inv_2",
      email: "emma@securitylabs.com",
      role: "Viewer",
      sentAt: new Date(Date.now() - 2 * 24 * 3600000).toISOString(),
    },
  ]);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  const getRoleColor = (role: string) => {
    switch (role) {
      case "Owner":
        return "bg-purple-500/20 text-purple-300 border-purple-500/30";
      case "Admin":
        return "bg-blue-500/20 text-blue-300 border-blue-500/30";
      case "Member":
        return "bg-green-500/20 text-green-300 border-green-500/30";
      case "Viewer":
        return "bg-gray-500/20 text-gray-300 border-gray-500/30";
      default:
        return "bg-gray-500/20 text-gray-300 border-gray-500/30";
    }
  };

  const getLastActiveText = (lastActive: string) => {
    const now = new Date();
    const then = new Date(lastActive);
    const diffMs = now.getTime() - then.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const handleInviteMember = () => {
    if (!inviteFormData.email) {
      alert("Please enter an email address");
      return;
    }
    setPendingInvites([
      ...pendingInvites,
      {
        id: `inv_${Date.now()}`,
        email: inviteFormData.email,
        role: inviteFormData.role,
        sentAt: new Date().toISOString(),
      },
    ]);
    setInviteFormData({ email: "", role: "Member" });
    setShowInviteModal(false);
    alert("Invitation sent!");
  };

  const handleRemoveMember = (memberId: string) => {
    if (confirm("Are you sure you want to remove this member?")) {
      setMembers(members.filter((m) => m.id !== memberId));
      alert("Member removed!");
    }
  };

  const handleChangeRole = (memberId: string, newRole: TeamMember["role"]) => {
    setMembers(
      members.map((m) =>
        m.id === memberId ? { ...m, role: newRole } : m
      )
    );
    alert("Role updated!");
  };

  const handleResendInvite = (inviteId: string) => {
    alert("Invitation resent!");
  };

  const handleCancelInvite = (inviteId: string) => {
    setPendingInvites(pendingInvites.filter((i) => i.id !== inviteId));
    alert("Invitation cancelled!");
  };

  if (!mounted) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Team Management</h1>
          <p className="text-gray-400">
            Manage team members and permissions ({members.length} members)
          </p>
        </div>
        <Button variant="primary" onClick={() => setShowInviteModal(true)}>
          Invite Member
        </Button>
      </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Invite Team Member</h3>
              <button
                onClick={() => setShowInviteModal(false)}
                className="text-gray-400 hover:text-gray-300"
              >
                ✕
              </button>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input
                label="Email Address"
                type="email"
                placeholder="user@example.com"
                value={inviteFormData.email}
                onChange={(e) =>
                  setInviteFormData({ ...inviteFormData, email: e.target.value })
                }
              />
              <div>
                <label className="block text-sm font-medium text-gray-200 mb-2">
                  Role
                </label>
                <select
                  value={inviteFormData.role}
                  onChange={(e) =>
                    setInviteFormData({
                      ...inviteFormData,
                      role: e.target.value as any,
                    })
                  }
                  className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white"
                >
                  <option>Owner</option>
                  <option>Admin</option>
                  <option>Member</option>
                  <option>Viewer</option>
                </select>
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <Button
                  variant="secondary"
                  onClick={() => setShowInviteModal(false)}
                >
                  Cancel
                </Button>
                <Button variant="primary" onClick={handleInviteMember}>
                  Send Invitation
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Team Members */}
      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold text-white">Team Members</h2>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">
                    Member
                  </th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">
                    Email
                  </th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">
                    Role
                  </th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">
                    Last Active
                  </th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">
                    2FA
                  </th>
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {members.map((member) => (
                  <tr
                    key={member.id}
                    className="border-b border-gray-800 hover:bg-gray-800/30 transition-colors"
                  >
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className="text-2xl">{member.avatar}</span>
                        <span className="text-white font-medium">
                          {member.name}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-gray-400">{member.email}</td>
                    <td className="py-3 px-4">
                      <select
                        value={member.role}
                        onChange={(e) =>
                          handleChangeRole(member.id, e.target.value as any)
                        }
                        className={`px-3 py-1 rounded-lg border text-sm font-medium ${getRoleColor(
                          member.role
                        )}`}
                      >
                        <option>Owner</option>
                        <option>Admin</option>
                        <option>Member</option>
                        <option>Viewer</option>
                      </select>
                    </td>
                    <td className="py-3 px-4 text-gray-400">
                      {getLastActiveText(member.lastActive)}
                    </td>
                    <td className="py-3 px-4">
                      {member.twoFaEnabled ? (
                        <Badge variant="success">Enabled</Badge>
                      ) : (
                        <Badge variant="warning">Disabled</Badge>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => handleRemoveMember(member.id)}
                        className="text-red-400 hover:text-red-300 text-sm font-medium"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Pending Invitations */}
      {pendingInvites.length > 0 && (
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-white">
              Pending Invitations
            </h2>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-800">
                    <th className="text-left py-3 px-4 text-gray-400 font-medium">
                      Email
                    </th>
                    <th className="text-left py-3 px-4 text-gray-400 font-medium">
                      Role
                    </th>
                    <th className="text-left py-3 px-4 text-gray-400 font-medium">
                      Sent
                    </th>
                    <th className="text-left py-3 px-4 text-gray-400 font-medium">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {pendingInvites.map((invite) => (
                    <tr
                      key={invite.id}
                      className="border-b border-gray-800 hover:bg-gray-800/30 transition-colors"
                    >
                      <td className="py-3 px-4 text-gray-300">{invite.email}</td>
                      <td className="py-3 px-4">
                        <Badge
                          variant={
                            invite.role === "Viewer" ? "warning" : "info"
                          }
                        >
                          {invite.role}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-gray-400">
                        {formatDate(invite.sentAt)}
                      </td>
                      <td className="py-3 px-4 space-x-2">
                        <button
                          onClick={() => handleResendInvite(invite.id)}
                          className="text-blue-400 hover:text-blue-300 text-sm font-medium"
                        >
                          Resend
                        </button>
                        <button
                          onClick={() => handleCancelInvite(invite.id)}
                          className="text-red-400 hover:text-red-300 text-sm font-medium"
                        >
                          Cancel
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Role Permissions Matrix */}
      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold text-white">
            Role Permissions Matrix
          </h2>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="text-left py-3 px-4 text-gray-400 font-medium">
                    Permission
                  </th>
                  <th className="text-center py-3 px-4 text-gray-400 font-medium">
                    Owner
                  </th>
                  <th className="text-center py-3 px-4 text-gray-400 font-medium">
                    Admin
                  </th>
                  <th className="text-center py-3 px-4 text-gray-400 font-medium">
                    Member
                  </th>
                  <th className="text-center py-3 px-4 text-gray-400 font-medium">
                    Viewer
                  </th>
                </tr>
              </thead>
              <tbody>
                {[
                  "Run Scans",
                  "View Results",
                  "Manage Team",
                  "Delete Organization",
                  "API Access",
                ].map((permission) => (
                  <tr
                    key={permission}
                    className="border-b border-gray-800 hover:bg-gray-800/30"
                  >
                    <td className="py-3 px-4 text-gray-300 font-medium">
                      {permission}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="text-green-400">✓</span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      {["Run Scans", "View Results", "API Access"].includes(
                        permission
                      ) ? (
                        <span className="text-green-400">✓</span>
                      ) : (
                        <span className="text-gray-500">—</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-center">
                      {["Run Scans", "View Results"].includes(permission) ? (
                        <span className="text-green-400">✓</span>
                      ) : (
                        <span className="text-gray-500">—</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-center">
                      {["View Results"].includes(permission) ? (
                        <span className="text-green-400">✓</span>
                      ) : (
                        <span className="text-gray-500">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
