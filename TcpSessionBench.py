#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TCP连接数限制测试工具
用于测试家庭宽带运营商对TCP连接数的限制
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socket
import threading
import time
import queue
from datetime import datetime


class TcpConnectionTester:
    """TCP连接测试器"""

    def __init__(self):
        self.running = False
        self.success_count = 0
        self.fail_count = 0
        self.total_attempts = 0
        self.lock = threading.Lock()
        self.threads = []
        self.start_time = None
        self.log_queue = queue.Queue()
        self.connections = []  # 保持连接不被关闭

    def reset_stats(self):
        """重置统计"""
        self.success_count = 0
        self.fail_count = 0
        self.total_attempts = 0
        self.connections = []
        self.start_time = time.time()

    def test_connection(self, host, port, timeout):
        """测试单个TCP连接"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            return True, sock
        except Exception as e:
            return False, str(e)

    def worker(self, host, port, timeout, interval, max_attempts, max_failures):
        """工作线程"""
        while self.running:
            with self.lock:
                if not self.running:
                    break
                if max_attempts > 0 and self.total_attempts >= max_attempts:
                    self.running = False
                    self.log_queue.put(("INFO", f"达到探测上限 ({max_attempts})，自动停止"))
                    break
                if max_failures > 0 and self.fail_count >= max_failures:
                    self.running = False
                    self.log_queue.put(("INFO", f"达到最大失败次数限制 ({max_failures})，停止探测"))
                    break
                self.total_attempts += 1
                current_attempt = self.total_attempts

            success, result = self.test_connection(host, port, timeout)

            with self.lock:
                if success:
                    self.success_count += 1
                    self.connections.append(result)  # 保持连接
                    status = "成功"
                else:
                    self.fail_count += 1
                    status = f"失败: {result}"

            elapsed = time.time() - self.start_time
            self.log_queue.put(("DEBUG", f"[{current_attempt}] TCP连接 {status} (用时: {elapsed:.2f}s)"))

            if interval > 0:
                time.sleep(interval)

    def start_test(self, host, port, session_count, interval, max_attempts, max_failures, timeout=5):
        """开始测试"""
        if self.running:
            return False

        self.running = True
        self.reset_stats()

        for i in range(session_count):
            t = threading.Thread(
                target=self.worker,
                args=(host, port, timeout, interval, max_attempts, max_failures)
            )
            t.daemon = True
            t.start()
            self.threads.append(t)

        return True

    def stop_test(self):
        """停止测试"""
        self.running = False

        # 关闭所有保持的连接
        for sock in self.connections:
            try:
                sock.close()
            except:
                pass
        self.connections = []

        # 等待线程结束
        for t in self.threads:
            try:
                t.join(timeout=1)
            except:
                pass
        self.threads = []

        return self.success_count, self.fail_count, time.time() - self.start_time if self.start_time else 0


class MainWindow:
    """主窗口"""

    def __init__(self, root):
        self.root = root
        self.root.title("TCP连接数限制测试工具V2.0")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        self.tester = TcpConnectionTester()
        self.update_job = None
        self.was_running = False  # 跟踪测试状态

        self.create_widgets()
        self.start_log_updater()

    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # ===== 配置区域 =====
        config_frame = ttk.LabelFrame(main_frame, text="测试配置", padding="10")
        config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        config_frame.columnconfigure(1, weight=1)
        config_frame.columnconfigure(3, weight=1)

        # 服务器地址
        ttk.Label(config_frame, text="服务器地址:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.host_var = tk.StringVar(value="223.6.6.6")
        ttk.Entry(config_frame, textvariable=self.host_var, width=25).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

        # 端口
        ttk.Label(config_frame, text="端口:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.port_var = tk.StringVar(value="53")
        ttk.Entry(config_frame, textvariable=self.port_var, width=10).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)

        # 会话数
        ttk.Label(config_frame, text="并发会话数:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.sessions_var = tk.StringVar(value="100")
        ttk.Entry(config_frame, textvariable=self.sessions_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(config_frame, text="个").grid(row=1, column=1, sticky=tk.W, padx=80)

        # 时间间隔
        ttk.Label(config_frame, text="连接间隔:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.interval_var = tk.StringVar(value="100")
        ttk.Entry(config_frame, textvariable=self.interval_var, width=10).grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        ttk.Label(config_frame, text="毫秒").grid(row=1, column=3, sticky=tk.W, padx=80)

        # 探测上限
        ttk.Label(config_frame, text="探测上限:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_attempts_var = tk.StringVar(value="10000")
        ttk.Entry(config_frame, textvariable=self.max_attempts_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(config_frame, text="0=无限制").grid(row=2, column=1, sticky=tk.W, padx=80)

        # 失败停止次数
        ttk.Label(config_frame, text="失败停止次数:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        self.max_failures_var = tk.StringVar(value="100")
        ttk.Entry(config_frame, textvariable=self.max_failures_var, width=10).grid(row=2, column=3, sticky=tk.W, padx=5, pady=5)
        ttk.Label(config_frame, text="0=不限制").grid(row=2, column=3, sticky=tk.W, padx=80)

        # 超时时间
        ttk.Label(config_frame, text="连接超时:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.timeout_var = tk.StringVar(value="5")
        ttk.Entry(config_frame, textvariable=self.timeout_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(config_frame, text="秒").grid(row=3, column=1, sticky=tk.W, padx=80)

        # ===== 控制按钮区域 =====
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        self.start_btn = ttk.Button(button_frame, text="▶ 开始测试", command=self.start_test, width=15)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(button_frame, text="⏹ 停止测试", command=self.stop_test, width=15, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(button_frame, text="🗑 清空日志", command=self.clear_log, width=15)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # ===== 统计区域 =====
        stats_frame = ttk.LabelFrame(main_frame, text="实时统计", padding="10")
        stats_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(3, weight=1)
        stats_frame.columnconfigure(5, weight=1)

        self.status_var = tk.StringVar(value="状态: 就绪")
        self.success_var = tk.StringVar(value="成功: 0")
        self.fail_var = tk.StringVar(value="失败: 0")
        self.elapsed_var = tk.StringVar(value="用时: 0.00s")

        ttk.Label(stats_frame, textvariable=self.status_var, font=("Arial", 10, "bold")).grid(row=0, column=0, padx=10)
        ttk.Label(stats_frame, textvariable=self.success_var, font=("Arial", 10), foreground="green").grid(row=0, column=1, padx=10)
        ttk.Label(stats_frame, textvariable=self.fail_var, font=("Arial", 10), foreground="red").grid(row=0, column=2, padx=10)
        ttk.Label(stats_frame, textvariable=self.elapsed_var, font=("Arial", 10)).grid(row=0, column=3, padx=10)

        # ===== 日志区域 =====
        log_frame = ttk.LabelFrame(main_frame, text="测试日志", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        main_frame.rowconfigure(3, weight=1)

        # 提示信息
        info_text = """使用说明:
1. 设置目标服务器和端口(默认使用百度80端口测试)
2. 调整线程数和连接间隔控制测试强度
3. 设置探测上限和失败停止次数保护系统
4. 点击"开始测试"启动连接数压力测试
5. 观察日志和统计信息，当连续失败增多时说明触发了限制

注意: 测试会消耗网络资源，请合理设置参数避免影响正常上网。"""
        ttk.Label(main_frame, text=info_text, justify=tk.LEFT, foreground="gray").grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)

    def log(self, message, level="INFO"):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        level_tags = {
            "INFO": ("blue",),
            "DEBUG": ("gray",),
            "SUCCESS": ("green",),
            "ERROR": ("red",)
        }

        self.log_text.insert(tk.END, f"[{timestamp}] [{level}] {message}\n")

        # 设置颜色标签
        if level == "SUCCESS":
            self.log_text.tag_add("success", f"{self.log_text.index(tk.END)}-2l linestart", f"{self.log_text.index(tk.END)}-2l lineend")
            self.log_text.tag_config("success", foreground="green")
        elif level == "ERROR":
            self.log_text.tag_add("error", f"{self.log_text.index(tk.END)}-2l linestart", f"{self.log_text.index(tk.END)}-2l lineend")
            self.log_text.tag_config("error", foreground="red")

        self.log_text.see(tk.END)

    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)

    def start_test(self):
        """开始测试"""
        try:
            host = self.host_var.get().strip()
            port = int(self.port_var.get())
            sessions = int(self.sessions_var.get())
            interval = float(self.interval_var.get()) / 1000.0  # 毫秒转秒
            max_attempts = int(self.max_attempts_var.get())
            max_failures = int(self.max_failures_var.get())
            timeout = float(self.timeout_var.get())

            if not host:
                messagebox.showerror("错误", "请输入服务器地址")
                return

            if sessions < 1:
                messagebox.showerror("错误", "会话数至少为1")
                return

            if port < 1 or port > 65535:
                messagebox.showerror("错误", "端口范围错误(1-65535)")
                return

            self.log(f"开始TCP连接数测试 - 目标: {host}:{port}", "INFO")
            self.log(f"参数: 会话数={sessions}, 间隔={interval*1000:.0f}ms, 上限={max_attempts if max_attempts > 0 else '无限制'}, 失败停止={max_failures if max_failures > 0 else '不限制'}", "INFO")

            if self.tester.start_test(host, port, sessions, interval, max_attempts, max_failures, timeout):
                self.was_running = True
                self.start_btn.config(state=tk.DISABLED)
                self.stop_btn.config(state=tk.NORMAL)
                self.status_var.set("状态: 运行中...")
            else:
                messagebox.showwarning("警告", "测试已经在运行中")

        except ValueError as e:
            messagebox.showerror("错误", f"参数格式错误: {e}\n请检查输入的数字格式")
        except Exception as e:
            messagebox.showerror("错误", f"启动失败: {e}")

    def stop_test(self):
        """停止测试"""
        self.log("正在停止测试...", "INFO")
        self.was_running = False
        success, fail, elapsed = self.tester.stop_test()

        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("状态: 已停止")

        self.log("=" * 50, "INFO")
        self.log(f"测试结束 - 成功: {success}, 失败: {fail}, 总计用时: {elapsed:.2f}秒", "INFO")
        self.log("=" * 50, "INFO")

        # 显示结果摘要
        result_msg = f"测试完成!\n\n成功连接: {success}\n失败连接: {fail}\n总用时: {elapsed:.2f}秒"
        if success > 0 and fail > 0 and fail / (success + fail) > 0.1:
            result_msg += "\n\n注意: 失败率较高，可能触发了运营商连接数限制"
        messagebox.showinfo("测试结果", result_msg)

    def start_log_updater(self):
        """启动日志更新器"""
        self.update_stats()
        self.update_log()

    def update_stats(self):
        """更新统计信息"""
        if self.tester.running:
            self.was_running = True
            elapsed = time.time() - self.tester.start_time if self.tester.start_time else 0
            self.success_var.set(f"成功: {self.tester.success_count}")
            self.fail_var.set(f"失败: {self.tester.fail_count}")
            self.elapsed_var.set(f"用时: {elapsed:.2f}s")
        elif self.was_running:
            # 测试自动停止了
            self.was_running = False
            self.auto_stop_test()

        self.update_job = self.root.after(100, self.update_stats)

    def auto_stop_test(self):
        """测试自动停止时的处理"""
        success, fail, elapsed = self.tester.stop_test()

        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("状态: 已完成")

        self.log("=" * 50, "INFO")
        self.log(f"测试自动结束 - 成功: {success}, 失败: {fail}, 总计用时: {elapsed:.2f}秒", "INFO")
        self.log("=" * 50, "INFO")

        # 显示结果摘要
        result_msg = f"测试完成!\n\n成功连接: {success}\n失败连接: {fail}\n总用时: {elapsed:.2f}秒"
        if success > 0 and fail > 0 and fail / (success + fail) > 0.1:
            result_msg += "\n\n注意: 失败率较高，可能触发了运营商连接数限制"
        messagebox.showinfo("测试结果", result_msg)

    def update_log(self):
        """更新日志"""
        try:
            while True:
                level, message = self.tester.log_queue.get_nowait()
                self.log(message, level)
        except queue.Empty:
            pass

        self.root.after(100, self.update_log)

    def on_closing(self):
        """关闭窗口时"""
        if self.tester.running:
            self.tester.stop_test()
        if self.update_job:
            self.root.after_cancel(self.update_job)
        self.root.destroy()


def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
