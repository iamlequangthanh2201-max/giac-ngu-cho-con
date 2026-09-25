# Giấc ngủ cho con

Sổ tay giấc ngủ cho trẻ 0–3 tuổi, và cho cả bố mẹ. Khung lấy từ 寝かしつけ *nekashitsuke* và chiến dịch 早寝早起き朝ごはん của Nhật, đối chiếu với nghiên cứu xuyên văn hoá của Mindell trên 29.287 trẻ ở 17 nước — trong đó Nhật, Hàn và Việt Nam cùng một cụm: đi ngủ muộn hơn, ngủ ít hơn phần còn lại. Nên sổ này **lấy nghi thức của Nhật, không lấy giờ đi ngủ của Nhật**.

Điểm khác các sách nuôi con khác: **giấc ngủ của bố mẹ là một chủ đề chính, đứng ngang với giấc ngủ của con** — không phải phụ lục, không phải "chịu đi rồi qua".

Cùng bộ với [Cẩm nang người cha](https://claude.ai/code/artifact/f37dbde6-2eae-493e-b31d-5caa2f23076a) *(EQ)*, [Nền tài chính cho con](https://claude.ai/code/artifact/06f23c50-7c3d-4594-a13e-cf59440b9e0c) và [Dinh dưỡng cho con](https://iamlequangthanh2201-max.github.io/dinh-duong-cho-con/).

## Nội dung

| File | Mục |
|---|---|
| `00-ngu-an-toan.md` | ⚠ Ngủ an toàn — sáu điều kiểm mỗi lần con ngủ *(ghim đầu mục lục)* |
| `01-nen-mong.md` | Nền móng — ba trụ, hai bảng ranh giới cứng |
| `02-truoc-khi-con-ra-doi.md` | Trước khi con ra đời — phòng, cũi, đồ mua, chia ca đêm |
| `03-nhip-ngay.md` | Nhịp ngày — số giờ thức, giấc ngày, giờ lên giường, ánh sáng |
| `04-dat-xuong.md` | Đặt xuống & tập tự ngủ — bảy cách kèm mức bằng chứng |
| `05-khi-con-thuc-dem.md` | Khi con thức đêm — khủng hoảng ngủ, ác mộng, sợ tối, dậy sớm |
| `06-giac-ngu-cua-bo-me.md` | Giấc ngủ của bố mẹ — chia ca, ngưỡng đổi ca, ngưỡng báo bác sĩ |
| `07-kich-ban.md` | 31 kịch bản — lọc theo tuổi và theo nhóm |
| `08-cong-cu-so.md` | Công cụ & sổ — nhật ký ngủ, bảng chia ca, Do & Don't |

## Dựng lại

```bash
python3 build.py
```

`build.py` ghép `styles.css` + `app.js` + các file `.md` thành hai bản: `index.html` để đăng làm Artifact riêng tư, và `docs/index.html` cho GitHub Pages. Không có bước build nào khác, không phụ thuộc gói ngoài.

## Cách viết

- Không đoạn văn dài. Mỗi hàng một việc làm được ngay: **một dòng tiêu đề, một dòng mô tả ngắn**
- Nhãn phải tự đứng được — không viết tắt kiểu phải biết trước mới hiểu
- Mỗi mục lớn có khối **Cơ sở** nói thật độ chắc của bằng chứng, tối đa năm gạch đầu dòng: chỗ nào là nghiên cứu đối chứng, chỗ nào là suy luận, chỗ nào là lựa chọn giá trị của gia đình
- Xanh lá = nên làm · nâu đất = nên tránh · tím khói = màu thương hiệu, không mang nghĩa cảnh báo

## Không thay bác sĩ

Sổ này lo **hậu cần trong nhà**: ai trực giờ nào, phòng bố trí ra sao, làm gì lúc 3 giờ sáng. Mọi dấu hiệu bất thường thì đi khám.
