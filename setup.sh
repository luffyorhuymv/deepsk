#!/bin/bash

# DeepSeek API Proxy - VPS Setup Script
# Hỗ trợ Ubuntu/Debian và CentOS/RHEL

set -e

# Màu sắc cho output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==============================================${NC}"
echo -e "${GREEN}   DeepSeek API Proxy - Tự Động Cài Đặt VPS   ${NC}"
echo -e "${GREEN}==============================================${NC}"

# Kiểm tra quyền root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Vui lòng chạy script với quyền root (sudo su)${NC}"
  exit 1
fi

# Phát hiện hệ điều hành
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
elif [ -f /etc/redhat-release ]; then
    OS="centos"
else
    OS="unknown"
fi

echo -e "${YELLOW} Hệ điều hành phát hiện: $OS${NC}"

# 1. Cập nhật hệ thống và cài đặt phụ thuộc
echo -e "${YELLOW}[1/4] Đang cài đặt các gói phụ thuộc...${NC}"
if [[ "$OS" == "ubuntu" || "$OS" == "debian" ]]; then
    apt-get update
    apt-get install -y python3 python3-pip python3-venv git curl docker.io docker-compose
elif [[ "$OS" == "centos" || "$OS" == "rhel" ]]; then
    yum update -y
    yum install -y python3 python3-pip git curl
    # Cài đặt Docker cho CentOS
    yum install -y yum-utils
    yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    systemctl start docker
    systemctl enable docker
else
    echo -e "${RED}Hệ điều hành không được hỗ trợ chính thức. Vui lòng cài đặt thủ công.${NC}"
fi

# 2. Thiết lập thư mục và tải code
echo -e "${YELLOW}[2/4] Thiết lập thư mục dự án...${NC}"
INSTALL_DIR="/opt/deepseek-api"
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR

# Nếu script được chạy từ file local, nó sẽ ở trong thư mục rồi. 
# Nếu chạy từ URL, chúng ta cần tải các file cần thiết.
if [ ! -f "proxy_server.py" ]; then
    echo -e "${YELLOW}Đang tải mã nguồn từ GitHub...${NC}"
    # Lưu ý: Ở đây chúng ta giả định người dùng đã clone repo hoặc chúng ta tải từng file.
    # Để đơn giản và chính xác nhất, khuyến khích người dùng clone repo trước khi chạy setup hoặc dùng git clone.
    echo -e "${RED}Lưu ý: Bạn nên chạy script này bên trong thư mục code đã clone.${NC}"
    echo -e "Nếu bạn muốn cài mới hoàn toàn, hãy nhập URL Git Repo (hoặc nhấn Enter để bỏ qua):"
    read GIT_URL
    if [ ! -z "$GIT_URL" ]; then
        cd /opt
        rm -rf deepseek-api
        git clone $GIT_URL deepseek-api
        cd deepseek-api
    fi
fi

# 3. Lựa chọn phương thức cài đặt
echo -e "${GREEN}Chọn phương thức cài đặt:${NC}"
echo "1) Docker Compose (Khuyến nghị - Nhanh & Ổn định)"
echo "2) Python Virtualenv (Cài trực tiếp lên OS)"
read -p "Nhập lựa chọn (1-2): " CHOICE

if [ "$CHOICE" == "1" ]; then
    echo -e "${YELLOW}[3/4] Đang khởi chạy bằng Docker Compose...${NC}"
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d --build
    else
        docker compose up -d --build
    fi
    echo -e "${GREEN}✅ Đã khởi chạy Docker container!${NC}"
else
    echo -e "${YELLOW}[3/4] Đang thiết lập Python Virtualenv...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
    
    # Tạo Systemd Service
    echo -e "${YELLOW}Đang tạo Systemd Service...${NC}"
    cat <<EOF > /etc/systemd/system/deepseek-api.service
[Unit]
Description=DeepSeek API Proxy Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/python proxy_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    systemctl enable deepseek-api
    systemctl start deepseek-api
    echo -e "${GREEN}✅ Đã tạo và khởi chạy Systemd Service!${NC}"
fi

# 4. Hoàn tất và hướng dẫn
echo -e "${GREEN}==============================================${NC}"
echo -e "${GREEN}        CÀI ĐẶT HOÀN TẤT THÀNH CÔNG!        ${NC}"
echo -e "${GREEN}==============================================${NC}"
IP_ADDR=$(curl -s https://ifconfig.me)
echo -e "API của bạn đang chạy tại: ${YELLOW}http://$IP_ADDR:5000${NC}"
echo -e ""
echo -e "Các bước tiếp theo:"
echo -e "1. Tạo API Key: ${CYAN}curl -X POST http://$IP_ADDR:5000/v1/keys/generate${NC}"
echo -e "2. Kiểm tra Logs: ${CYAN}journalctl -u deepseek-api -f${NC} (nếu dùng Systemd)"
echo -e "   hoặc ${CYAN}docker logs -f deepseek-proxy${NC} (nếu dùng Docker)"
echo -e ""
echo -e "${YELLOW}Cảm ơn bạn đã sử dụng DeepSeek API Proxy!${NC}"
