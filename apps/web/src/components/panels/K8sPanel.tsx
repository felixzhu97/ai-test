import { AgentChat } from '../agents/AgentChat';
import { AgentPanel } from './AgentPanel';
import { StatusBadge } from '../agents/StatusBadge';
import { useI18n } from '../../i18n';

const AGENT_INFO = {
  status: 'online' as const,
};

export function K8sPanel() {
  const { t } = useI18n();
  return (
    <AgentPanel
      title={t.nav.kubernetes}
      description={t.agents.descriptions.k8s}
      headerRight={<StatusBadge status={AGENT_INFO.status} />}
    >
      <AgentChat
        agentInfo={{ name: t.nav.kubernetes, description: t.agents.descriptions.k8s }}
        apiEndpoint="/api/agents/kubernetes/invoke"
        quickPrompts={t.agents.quickPrompts.k8s}
      />
    </AgentPanel>
  );
}
