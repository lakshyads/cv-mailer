import { Fragment } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/atoms/ui/Card';
import { Spinner } from '@/components/atoms/ui/Spinner';
import { ProgressTracker } from '@/components/organisms/shared/ProgressTracker';
import { SortableTableHeader } from '@/components/molecules/SortableTableHeader';
import { ApplicationsTableRow } from '@/components/organisms/applications/ApplicationsTableRow';
import { Send, MoreVertical } from 'lucide-react';
import type { Application, JobStatus } from '@/types';

type SortField = 'created_at' | 'updated_at' | 'status' | null;
type SortOrder = 'asc' | 'desc';

interface ApplicationsTableProps {
  applications: Application[];
  total: number;
  isLoading: boolean;
  error: Error | null;
  searchQuery: string;
  sortBy: SortField;
  sortOrder: SortOrder;
  onSort: (field: SortField) => void;
  expandedRows: Set<number>;
  onToggleRow: (id: number) => void;
  showProgressTracker: boolean;
  actionMenuOpen: number | null;
  onActionMenuToggle: (id: number | null) => void;
  onTriggerReachOut: (id: number) => void;
  onTriggerFollowUp: (id: number) => void;
  onUpdateStatus: (id: number, status: string) => void;
  isTriggeringReachOut: (id: number) => boolean;
  isTriggeringFollowUp: (id: number) => boolean;
  isUpdatingStatus: (id: number) => boolean;
  getValidNextStatuses: (status: JobStatus) => JobStatus[];
}

/**
 * Applications table component.
 * Displays applications in a sortable, expandable table with actions.
 */
export function ApplicationsTable({
  applications,
  total,
  isLoading,
  error,
  searchQuery,
  sortBy,
  sortOrder,
  onSort,
  expandedRows,
  onToggleRow,
  showProgressTracker,
  actionMenuOpen,
  onActionMenuToggle,
  onTriggerReachOut,
  onTriggerFollowUp,
  onUpdateStatus,
  isTriggeringReachOut,
  isTriggeringFollowUp,
  isUpdatingStatus,
  getValidNextStatuses,
}: ApplicationsTableProps) {

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          {total} Application{total !== 1 ? 's' : ''}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="py-12">
            <Spinner />
          </div>
        ) : error ? (
          <div className="py-12 text-center text-red-600">
            Error loading applications. Please try again.
          </div>
        ) : applications.length === 0 ? (
          <div className="py-12 text-center text-muted-foreground">
            {searchQuery
              ? 'No applications found matching your search.'
              : 'No applications found.'}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-semibold text-sm w-8"></th>
                  <th className="text-left py-3 px-4 font-semibold text-sm">
                    <button
                      onClick={() => onSort(null)}
                      className="flex items-center gap-2 hover:text-primary transition-colors"
                    >
                      Company / Position
                    </button>
                  </th>
                  <SortableTableHeader
                    field="status"
                    currentSort={sortBy}
                    currentOrder={sortOrder}
                    onSort={onSort}
                  >
                    Status
                  </SortableTableHeader>
                  <SortableTableHeader
                    field="created_at"
                    currentSort={sortBy}
                    currentOrder={sortOrder}
                    onSort={onSort}
                  >
                    Created
                  </SortableTableHeader>
                  <SortableTableHeader
                    field="updated_at"
                    currentSort={sortBy}
                    currentOrder={sortOrder}
                    onSort={onSort}
                  >
                    Last Updated
                  </SortableTableHeader>
                  <th className="text-left py-3 px-4 font-semibold text-sm">Emails</th>
                  <th className="text-right py-3 px-4 font-semibold text-sm">Actions</th>
                </tr>
              </thead>
              <tbody>
                {applications.map((app) => {
                  const isExpanded = expandedRows.has(app.id);
                  const validNextStatuses = getValidNextStatuses(app.status);
                  return (
                    <Fragment key={app.id}>
                      <ApplicationsTableRow
                        application={app}
                        showExpandButton={true}
                        isExpanded={isExpanded}
                        onToggleExpand={() => onToggleRow(app.id)}
                        showCreatedAt={true}
                        showActions={true}
                        showLocation={true}
                        showJobUrl={true}
                        size="md"
                        actions={
                          <div className="flex items-center justify-end gap-2">
                            <div className="relative">
                              <button
                                onClick={() =>
                                  onActionMenuToggle(actionMenuOpen === app.id ? null : app.id)
                                }
                                className="p-1 hover:bg-muted rounded transition-colors"
                                aria-label="More actions"
                                data-app-id={app.id}
                              >
                                <MoreVertical className="h-4 w-4 text-muted-foreground" />
                              </button>
                              {actionMenuOpen === app.id && (
                                <div className="absolute right-0 top-full mt-1 z-50 w-48 rounded-md border bg-popover shadow-lg">
                                  <div className="p-1">
                                    <button
                                      onClick={() => {
                                        onTriggerReachOut(app.id);
                                        onActionMenuToggle(null);
                                      }}
                                      disabled={isTriggeringReachOut(app.id)}
                                      className="w-full text-left px-3 py-2 text-sm rounded-md hover:bg-muted flex items-center gap-2 disabled:opacity-50"
                                    >
                                      <Send className="h-4 w-4" />
                                      {isTriggeringReachOut(app.id) ? 'Sending...' : 'Reach Out'}
                                    </button>
                                    <button
                                      onClick={() => {
                                        onTriggerFollowUp(app.id);
                                        onActionMenuToggle(null);
                                      }}
                                      disabled={isTriggeringFollowUp(app.id)}
                                      className="w-full text-left px-3 py-2 text-sm rounded-md hover:bg-muted flex items-center gap-2 disabled:opacity-50"
                                    >
                                      <Send className="h-4 w-4" />
                                      {isTriggeringFollowUp(app.id) ? 'Sending...' : 'Follow Up'}
                                    </button>
                                    {validNextStatuses.length > 0 && (
                                      <>
                                        <div className="px-2 py-1 text-xs font-medium text-muted-foreground">
                                          Quick Status:
                                        </div>
                                        {validNextStatuses.map((status) => (
                                          <button
                                            key={status}
                                            onClick={() => {
                                              onUpdateStatus(app.id, status);
                                              onActionMenuToggle(null);
                                            }}
                                            disabled={isUpdatingStatus(app.id)}
                                            className="w-full text-left px-3 py-2 text-xs rounded-md hover:bg-muted disabled:opacity-50"
                                          >
                                            {status.replace(/_/g, ' ').replace(/\b\w/g, (l) =>
                                              l.toUpperCase()
                                            )}
                                          </button>
                                        ))}
                                      </>
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        }
                      />
                      {(isExpanded || showProgressTracker) && (
                        <tr>
                          <td colSpan={7} className="py-4 px-4 bg-muted/30">
                            <ProgressTracker
                              currentStatus={app.status}
                              lastMainFlowStatus={app.last_main_flow_status}
                            />
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}


