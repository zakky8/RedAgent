'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  AlertCircle,
  Bug,
  Check,
  Clock,
  Database,
  Loader2,
  Shield,
} from 'lucide-react';

interface Vulnerability {
  cve_id: string;
  name: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  cvss_score: number;
  description: string;
  remediation: string;
}

interface ServiceInfo {
  name: string;
  version: string;
  is_public: boolean;
  known_vulnerabilities: number;
}

interface ScanResult {
  service_info: ServiceInfo;
  vulnerabilities: Vulnerability[];
  misconfigurations: string[];
  overall_risk: string;
}

export default function InfraPage() {
  const router = useRouter();
  const [targetUrl, setTargetUrl] = useState('');
  const [serviceType, setServiceType] = useState('');
  const [scanning, setScanning] = useState(false);
  const [results, setResults] = useState<ScanResult | null>(null);
  const [detectedService, setDetectedService] = useState<ServiceInfo | null>(null);

  const serviceTypes = [
    'ollama',
    'comfyui',
    'vllm',
    'gradio',
    'ray',
    'jupyter',
    'mlflow',
    'langserve',
    'bentoml',
    'localai',
  ];

  const handleScan = async () => {
    if (!targetUrl) return;

    setScanning(true);
    try {
      const response = await fetch('/api/v1/infra/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_url: targetUrl,
          service_type: serviceType || undefined,
          deep_scan: true,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data);
      }
    } catch (error) {
      console.error('Scan failed:', error);
    } finally {
      setScanning(false);
    }
  };

  const handleDetect = async () => {
    if (!targetUrl) return;

    try {
      const response = await fetch(
        `/api/v1/infra/detect?target_url=${encodeURIComponent(targetUrl)}`
      );

      if (response.ok) {
        const data = await response.json();
        setDetectedService(data.service);
      }
    } catch (error) {
      console.error('Detection failed:', error);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'text-red-600 bg-red-50';
      case 'high':
        return 'text-orange-600 bg-orange-50';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50';
      case 'low':
        return 'text-green-600 bg-green-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          AI Infrastructure Scanner
        </h1>
        <p className="text-gray-600 mt-2">
          Scan AI services (Ollama, ComfyUI, vLLM, etc.) for CVEs and misconfigurations
        </p>
      </div>

      <Tabs defaultValue="scan" className="w-full">
        <TabsList>
          <TabsTrigger value="scan">Scanner</TabsTrigger>
          <TabsTrigger value="cves">Known CVEs</TabsTrigger>
          <TabsTrigger value="config">Configuration Audit</TabsTrigger>
        </TabsList>

        <TabsContent value="scan">
          <Card>
            <CardHeader>
              <CardTitle>Scan Infrastructure Service</CardTitle>
              <CardDescription>
                Provide the URL of an exposed AI service to scan for vulnerabilities
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="target-url">Target URL</Label>
                  <Input
                    id="target-url"
                    placeholder="http://localhost:11434 or https://api.example.com/ollama"
                    value={targetUrl}
                    onChange={(e) => setTargetUrl(e.target.value)}
                  />
                </div>

                <div>
                  <Label htmlFor="service-type">Service Type (Optional)</Label>
                  <select
                    id="service-type"
                    className="w-full px-3 py-2 border rounded-md"
                    value={serviceType}
                    onChange={(e) => setServiceType(e.target.value)}
                  >
                    <option value="">Auto-detect</option>
                    {serviceTypes.map((type) => (
                      <option key={type} value={type}>
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex gap-2">
                  <Button onClick={handleDetect} variant="outline">
                    Detect Service
                  </Button>
                  <Button
                    onClick={handleScan}
                    disabled={!targetUrl || scanning}
                  >
                    {scanning ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Scanning...
                      </>
                    ) : (
                      <>
                        <Shield className="mr-2 h-4 w-4" />
                        Scan
                      </>
                    )}
                  </Button>
                </div>
              </div>

              {detectedService && (
                <Card className="bg-blue-50 border-blue-200">
                  <CardContent className="pt-6">
                    <p className="font-semibold text-blue-900">
                      {detectedService.name} {detectedService.version}
                    </p>
                    <p className="text-sm text-blue-700">
                      {detectedService.is_public
                        ? '⚠️ Publicly Exposed'
                        : '✓ Private'}
                    </p>
                  </CardContent>
                </Card>
              )}

              {results && (
                <div className="space-y-4 mt-6">
                  <h3 className="font-semibold text-lg">Scan Results</h3>

                  <div className="grid grid-cols-3 gap-4">
                    <Card>
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">
                            Total CVEs
                          </span>
                          <Bug className="h-5 w-5 text-red-600" />
                        </div>
                        <p className="text-2xl font-bold mt-2">
                          {results.vulnerabilities.length}
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">
                            Risk Level
                          </span>
                          <AlertCircle
                            className={`h-5 w-5 ${
                              results.overall_risk === 'critical'
                                ? 'text-red-600'
                                : 'text-yellow-600'
                            }`}
                          />
                        </div>
                        <p className="text-2xl font-bold mt-2 uppercase">
                          {results.overall_risk}
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">
                            Config Issues
                          </span>
                          <Database className="h-5 w-5 text-orange-600" />
                        </div>
                        <p className="text-2xl font-bold mt-2">
                          {results.misconfigurations.length}
                        </p>
                      </CardContent>
                    </Card>
                  </div>

                  <div>
                    <h4 className="font-semibold mb-3">Vulnerabilities</h4>
                    <div className="space-y-2">
                      {results.vulnerabilities.map((vuln) => (
                        <Card
                          key={vuln.cve_id}
                          className={getSeverityColor(vuln.severity)}
                        >
                          <CardContent className="pt-4">
                            <p className="font-semibold">{vuln.cve_id}</p>
                            <p className="text-sm">{vuln.name}</p>
                            <p className="text-sm font-mono">
                              CVSS: {vuln.cvss_score}
                            </p>
                            <p className="text-xs mt-2">{vuln.remediation}</p>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="cves">
          <Card>
            <CardHeader>
              <CardTitle>Known CVE Database</CardTitle>
              <CardDescription>
                Browse CVEs affecting common AI infrastructure
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Select a service to view known CVEs for that infrastructure.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="config">
          <Card>
            <CardHeader>
              <CardTitle>Configuration Audit</CardTitle>
              <CardDescription>
                Check for common misconfigurations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Configuration audit results will appear here after scanning.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
