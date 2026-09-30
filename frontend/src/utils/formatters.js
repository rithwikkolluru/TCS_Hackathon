export function formatNumber(num) {
  if (num === null || num === undefined) return "0";
  return new Intl.NumberFormat("en-IN").format(num);
}

export function formatMinutes(mins) {
  if (mins === null || mins === undefined) return "0m";
  const num = Number(mins);
  if (isNaN(num)) return "0m";
  if (num < 1) return `${Math.round(num * 60)}s`;
  if (num >= 60) {
    const hours = Math.floor(num / 60);
    const remain = Math.round(num % 60);
    return `${hours}h ${remain}m`;
  }
  return `${num.toFixed(1)}m`;
}

export function formatDateTime(dateStr) {
  if (!dateStr) return "-";
  try {
    const d = new Date(dateStr);
    return d.toLocaleString("en-IN", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  } catch (e) {
    return dateStr;
  }
}

export function formatTime(timeStr) {
  if (!timeStr) return "-";
  try {
    const d = new Date(timeStr);
    if (!isNaN(d.getTime())) {
      return d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    }
    return timeStr;
  } catch (e) {
    return timeStr;
  }
}

export function getRiskColor(risk) {
  switch (String(risk).toUpperCase()) {
    case "CRITICAL":
      return "#f43f5e";
    case "HIGH":
      return "#fb923c";
    case "MEDIUM":
      return "#f59e0b";
    case "LOW":
    default:
      return "#10b981";
  }
}
