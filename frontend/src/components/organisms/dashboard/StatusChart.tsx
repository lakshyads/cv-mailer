import { Card, CardContent, CardHeader, CardTitle } from '@/components/atoms/ui/Card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { CHART_STATUS_COLORS, prepareStatusBarData, calculateYAxisDomain } from '@/lib/chartUtils';
import type { Statistics } from '@/types';

interface StatusChartProps {
    stats: Statistics;
}

/**
 * Application status overview chart component.
 */
export function StatusChart({ stats }: StatusChartProps) {
    const statusBarData = prepareStatusBarData(stats);
    const yAxisDomain = calculateYAxisDomain(statusBarData);

    return (
        <Card className="lg:col-span-2">
            <CardHeader>
                <CardTitle>Application Status Overview</CardTitle>
            </CardHeader>
            <CardContent className="pb-2">
                <div className="h-[606px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={statusBarData} margin={{ top: 10, right: 20, left: 10, bottom: 80 }}>
                            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" opacity={0.3} />
                            <XAxis
                                dataKey="status"
                                className="text-xs"
                                interval={0}
                                angle={-45}
                                textAnchor="end"
                                height={80}
                                tick={{ fill: 'currentColor', className: 'fill-muted-foreground', fontSize: 10 }}
                            />
                            <YAxis
                                className="text-xs"
                                tick={{ fill: 'currentColor', className: 'fill-muted-foreground', fontSize: 11 }}
                                domain={yAxisDomain}
                                allowDecimals={false}
                                width={30}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'hsl(var(--card))',
                                    border: '1px solid hsl(var(--border))',
                                    borderRadius: '8px',
                                    boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                                }}
                                labelStyle={{ color: 'hsl(var(--foreground))' }}
                            />
                            <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                                {statusBarData.map((entry, index) => (
                                    <Cell
                                        key={`cell-${index}`}
                                        fill={CHART_STATUS_COLORS[entry.statusKey] || '#3b82f6'}
                                    />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    );
}

