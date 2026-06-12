#!/usr/bin/env bash
LOG_FILE="${HOME}/nina/logs/gemini_wrapper.log"
REFRESH=2
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; WHITE='\033[1;37m'; DIM='\033[2m'; RESET='\033[0m'; BOLD='\033[1m'

draw_bar() {
  local val=$1 max=$2 width=$3 color=$4
  local filled=$(( val * width / (max > 0 ? max : 1) ))
  [ $filled -gt $width ] && filled=$width
  local empty=$(( width - filled ))
  printf "${color}"; printf '%*s' "$filled" '' | tr ' ' '█'
  printf "${DIM}";   printf '%*s' "$empty"  '' | tr ' ' '░'
  printf "${RESET}"
}

get_gemini_pid()  { pgrep -f "gemini" 2>/dev/null | head -1; }
get_cpu_temp()    { local t; t=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null); [ -n "$t" ] && echo "$(( t / 1000 ))°C" || echo "N/A"; }
get_gpu_temp()    { nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits 2>/dev/null | head -1 | xargs -I{} echo "{}°C" || echo "N/A"; }
get_ram_usage()   { free -m | awk '/^Mem:/ {printf "%d/%dMB (%.0f%%)", $3, $2, $3/$2*100}'; }
get_cpu_usage()   { top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1; }
get_last_stall()  { grep "STALL" "$LOG_FILE" 2>/dev/null | tail -1 | awk '{print $1,$2}' || echo "none"; }

get_active_task() {
  local pid; pid=$(get_gemini_pid)
  [ -n "$pid" ] && ps -p "$pid" -o args= 2>/dev/null | sed 's/gemini//' | cut -c1-65 || echo "idle"
}

get_process_runtime() {
  local pid; pid=$(get_gemini_pid)
  if [ -n "$pid" ]; then
    local s; s=$(ps -p "$pid" -o etimes= 2>/dev/null | tr -d ' ')
    [ -n "$s" ] && printf "%dm %ds" "$(( s/60 ))" "$(( s%60 ))"
  else echo "--"; fi
}

get_timeout_remaining() {
  local pid; pid=$(get_gemini_pid)
  if [ -n "$pid" ]; then
    local tmt="${GEMINI_TIMEOUT:-120}"
    local el; el=$(ps -p "$pid" -o etimes= 2>/dev/null | tr -d ' ')
    if [ -n "$el" ]; then
      local r=$(( tmt - el ))
      if   [ "$r" -le 0  ]; then echo -e "${RED}OVERDUE!${RESET}"
      elif [ "$r" -le 20 ]; then echo -e "${RED}${r}s${RESET}"
      elif [ "$r" -le 45 ]; then echo -e "${YELLOW}${r}s${RESET}"
      else                        echo -e "${GREEN}${r}s${RESET}"; fi
    fi
  else echo "--"; fi
}

get_recent_log() { tail -8 "$LOG_FILE" 2>/dev/null || echo "  (no log yet)"; }

get_stats() {
  local total stalls ok
  total=$(grep -c "Starting gemini\|Scoped gemini" "$LOG_FILE" 2>/dev/null || echo 0)
  stalls=$(grep -c "STALL" "$LOG_FILE" 2>/dev/null || echo 0)
  ok=$(grep -c "exit 0" "$LOG_FILE" 2>/dev/null || echo 0)
  echo "$total $stalls $ok"
}

render() {
  clear
  local pid; pid=$(get_gemini_pid)
  local running=false; [ -n "$pid" ] && running=true

  local cpu_temp gpu_temp ram cpu_usage
  cpu_temp=$(get_cpu_temp); gpu_temp=$(get_gpu_temp)
  ram=$(get_ram_usage);     cpu_usage=$(get_cpu_usage); cpu_usage="${cpu_usage:-0}"

  local quota_used
  quota_used=$(grep "$(date '+%Y-%m-%d')" "$LOG_FILE" 2>/dev/null | grep -c "Starting gemini\|Scoped gemini" || echo 0)

  read -r total stalls ok <<< "$(get_stats)"

  echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════════╗${RESET}"
  echo -e "${BOLD}${CYAN}║        NINA · Gemini CLI Monitor                             ║${RESET}"
  printf  "${BOLD}${CYAN}║        %-52s║${RESET}\n" "$(date '+%Y-%m-%d %H:%M:%S')   refresh: ${REFRESH}s"
  echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════════╝${RESET}"
  echo

  if $running; then
    echo -e "  ${BOLD}STATUS${RESET}  ${GREEN}● RUNNING${RESET}  PID:${WHITE}$pid${RESET}  Runtime:${WHITE}$(get_process_runtime)${RESET}  Timeout in: $(get_timeout_remaining)"
  else
    echo -e "  ${BOLD}STATUS${RESET}  ${DIM}○ IDLE${RESET}   last stall: ${DIM}$(get_last_stall)${RESET}"
  fi
  echo
  echo -e "  ${BOLD}TASK${RESET}    ${YELLOW}$(get_active_task)${RESET}"
  echo

  echo -e "  ${BOLD}${WHITE}── Hardware ──────────────────────────────────────────────────${RESET}"
  local n c
  n=$(echo "$cpu_temp" | tr -d '°C'); [[ "$n" =~ ^[0-9]+$ ]] || n=0
  c=$GREEN; [ "$n" -ge 75 ] && c=$YELLOW; [ "$n" -ge 85 ] && c=$RED
  printf "  %-10s %s  $(echo -e "${c}%s${RESET}")\n" "CPU Temp" "$(draw_bar $n 100 30 $c)" "$cpu_temp"

  n=$(echo "$gpu_temp" | tr -d '°C'); [[ "$n" =~ ^[0-9]+$ ]] || n=0
  c=$GREEN; [ "$n" -ge 70 ] && c=$YELLOW; [ "$n" -ge 80 ] && c=$RED
  printf "  %-10s %s  $(echo -e "${c}%s${RESET}")\n" "GPU Temp" "$(draw_bar $n 100 30 $c)" "$gpu_temp"

  n=${cpu_usage%.*}; [[ "$n" =~ ^[0-9]+$ ]] || n=0
  c=$GREEN; [ "$n" -ge 60 ] && c=$YELLOW; [ "$n" -ge 85 ] && c=$RED
  printf "  %-10s %s  $(echo -e "${c}%s${RESET}")\n" "CPU Load" "$(draw_bar $n 100 30 $c)" "${cpu_usage}%"

  echo -e "  ${DIM}RAM        $ram${RESET}"
  echo

  echo -e "  ${BOLD}${WHITE}── Quota (resets 1PM BD) ─────────────────────────────────────${RESET}"
  c=$GREEN; [ "$quota_used" -ge 700 ] && c=$YELLOW; [ "$quota_used" -ge 900 ] && c=$RED
  printf "  %-10s %s  $(echo -e "${c}%s${RESET}")\n" "Today" "$(draw_bar $quota_used 1000 30 $c)" "${quota_used}/1000 req"
  echo

  echo -e "  ${BOLD}${WHITE}── Stats ─────────────────────────────────────────────────────${RESET}"
  echo -e "  Runs: ${WHITE}${total:-0}${RESET}   Success: ${GREEN}${ok:-0}${RESET}   Stalls: ${RED}${stalls:-0}${RESET}"
  echo

  echo -e "  ${BOLD}${WHITE}── Recent Log ────────────────────────────────────────────────${RESET}"
  get_recent_log | while IFS= read -r line; do
    if   echo "$line" | grep -q "STALL";            then echo -e "  ${RED}${line}${RESET}"
    elif echo "$line" | grep -q "exit 0";           then echo -e "  ${GREEN}${line}${RESET}"
    elif echo "$line" | grep -q "Starting\|Scoped"; then echo -e "  ${YELLOW}${line}${RESET}"
    else                                                 echo -e "  ${DIM}${line}${RESET}"; fi
  done
  echo
  echo -e "  ${DIM}Ctrl+C to exit  │  $LOG_FILE${RESET}"
}

mkdir -p "${HOME}/nina/logs"
touch "$LOG_FILE" 2>/dev/null
while true; do render; sleep "$REFRESH"; done
