import sys
import json
import subprocess
import os

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    # Basic MCP stdio server skeleton
    # For now, we'll just handle tools via a simple dispatcher if called as a script,
    # or implement the full JSON-RPC if needed by Gemini CLI.
    # Gemini CLI MCP extensions typically expect a JSON-RPC server.
    
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            request = json.loads(line)
            # Handle JSON-RPC request (simplistic)
            method = request.get("method")
            params = request.get("params", {})
            req_id = request.get("id")
            
            if method == "listTools":
                result = {
                    "tools": [
                        {"name": "nf", "description": "Run ninaflash command", "inputSchema": {"type": "object", "properties": {"args": {"type": "string"}}}},
                        {"name": "status", "description": "Check NINA service status", "inputSchema": {"type": "object", "properties": {}}},
                        {"name": "sync", "description": "Run nina_sync.sh", "inputSchema": {"type": "object", "properties": {}}}
                    ]
                }
            elif method == "callTool":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                if tool_name == "nf":
                    cmd = f"nf {tool_args.get('args', '')}"
                    res = run_command(cmd)
                    result = {"content": [{"type": "text", "text": f"STDOUT: {res.get('stdout')}\nSTDERR: {res.get('stderr')}"}]}
                elif tool_name == "status":
                    cmd = "systemctl status nina --no-pager && tail -n 20 logs/ninagate.log"
                    res = run_command(cmd)
                    result = {"content": [{"type": "text", "text": res.get("stdout") or res.get("stderr")}]}
                elif tool_name == "sync":
                    cmd = "./nina_sync.sh"
                    res = run_command(cmd)
                    result = {"content": [{"type": "text", "text": res.get("stdout")}]}
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}
            else:
                result = {"error": f"Unknown method: {method}"}
                
            response = {"jsonrpc": "2.0", "id": req_id, "result": result}
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            
        except Exception as e:
            # sys.stderr.write(f"Error: {e}\n")
            pass

if __name__ == "__main__":
    main()
