FROM band_subscriber

ENV DEBUG=true
ENV BAND_ADDRESS=0x382fAD953a2F2f38E506f1Aad1D18fAC39f390c3

CMD ["./initialize.sh"]
