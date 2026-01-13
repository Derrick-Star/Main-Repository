import qrcode

data = "https://termux.dev/community"  # Replace with your URL or text


qr = qrcode.QRCode(
    version=1,  # Controls size of the QR Code (1 = 21x21)
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)


qr.add_data(data)
qr.make(fit=True)


img = qr.make_image(fill_color="black", back_color="white")

img.save("my_qrcode.png")

print("QR Code generated and saved as my_qrcode.png")
