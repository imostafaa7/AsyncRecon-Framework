#!/usr/bin/env python3
import asyncio
import argparse
import socket
import sys
import resource
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

console = Console()

def set_file_limit():
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))
        return hard
    except Exception as e:
        console.print(f"[!] تحذير: لم يتمكن السكربت من رفع حدود واصفات الملفات (FD Limit): {e}", style="yellow")
        return None

async def scan_port(semaphore, target, port, timeout):
    async with semaphore:
        try:
            conn = asyncio.open_connection(target, port)
            reader, writer = await asyncio.wait_for(conn, timeout=timeout)
            
            banner = ""
            try:
                # محاولة قراءة الترويسة (Banner Grabbing)
                data = await asyncio.wait_for(reader.read(1024), timeout=0.5)
                banner = data.decode('utf-8', errors='ignore').strip().replace('\r', '').replace('\n', '\\n')
            except asyncio.TimeoutError:
                pass
            finally:
                writer.close()
                await writer.wait_closed()
                
            return port, True, banner
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return port, False, ""

async def main(target, concurrency, timeout, start_port, end_port):
    limit = set_file_limit()
    actual_concurrency = min(concurrency, limit) if limit else concurrency
    
    semaphore = asyncio.Semaphore(actual_concurrency)
    ports_to_scan = range(start_port, end_port + 1)
    total_ports = len(ports_to_scan)
    
    open_ports = []

    banner_text = Text(f"Asynchronous Port Scanner\nالهدف: {target} | التزامن: {actual_concurrency} | المنافذ: {total_ports}", style="bold cyan", justify="center")
    console.print(Panel(banner_text, border_style="blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        scan_task = progress.add_task("[cyan]جاري الفحص...", total=total_ports)
        
        tasks = [
            asyncio.create_task(scan_port(semaphore, target, port, timeout))
            for port in ports_to_scan
        ]
        
        for coro in asyncio.as_completed(tasks):
            port, is_open, banner = await coro
            progress.update(scan_task, advance=1)
            
            if is_open:
                open_ports.append((port, banner))
                # طباعة فورية فوق شريط التقدم
                if banner:
                    progress.console.print(f"[+] [green]منفذ مفتوح:[/green] {port:<5} | [yellow]الترويسة:[/yellow] {banner[:50]}")
                else:
                    progress.console.print(f"[+] [green]منفذ مفتوح:[/green] {port:<5}")

    # النتائج النهائية
    if open_ports:
        open_ports.sort(key=lambda x: x[0])
        table = Table(title=f"نتائج الفحص النهائي - {target}", style="bold magenta")
        table.add_column("المنفذ", justify="right", style="cyan", no_wrap=True)
        table.add_column("الحالة", style="green")
        table.add_column("الترويسة (Banner)", style="yellow")
        
        for port, banner in open_ports:
            table.add_row(str(port), "مفتوح", banner if banner else "-")
            
        console.print(table)
    else:
        console.print(Panel("[-] لم يتم العثور على منافذ مفتوحة.", style="bold red"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="High-Speed Async Port Scanner")
    parser.add_argument("-t", "--target", required=True, help="عنوان IP المستهدف (مثال: 192.168.1.1)")
    parser.add_argument("-c", "--concurrency", type=int, default=1000, help="عدد الاتصالات المتزامنة (الافتراضي 1000)")
    parser.add_argument("-to", "--timeout", type=float, default=1.5, help="مهلة الاتصال بالثانية (الافتراضي 1.5)")
    parser.add_argument("-s", "--start", type=int, default=1, help="بداية نطاق المنافذ")
    parser.add_argument("-e", "--end", type=int, default=65535, help="نهاية نطاق المنافذ")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main(args.target, args.concurrency, args.timeout, args.start, args.end))
    except KeyboardInterrupt:
        console.print("\n[!] تم إيقاف الفحص من قبل المستخدم.", style="bold red")
        sys.exit(0)
