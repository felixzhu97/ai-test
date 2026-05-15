import { AgentChat } from '../agents/AgentChat';
import { AgentPanel } from './AgentPanel';
import { StatusBadge } from '../agents/StatusBadge';
import { useI18n } from '../../i18n';

const AGENT_INFO = {
  status: 'online' as const,
};

export function VectorDBPanel() {
  const { t } = useI18n();
  return (
    <AgentPanel
      title={t.nav.vectordb}
      description={t.agents.descriptions.vectordb}
      headerRight={<StatusBadge status={AGENT_INFO.status} />}
    >
      <AgentChat
        agentInfo={{ name: t.nav.vectordb, description: t.agents.descriptions.vectordb }}
        apiEndpoint="/api/agents/vector/invoke"
        quickPrompts={t.agents.quickPrompts.vectordb}
      />
    </AgentPanel>
  );
}
