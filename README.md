## Face-ID (FACE IDentification)

#### 训练
`python3 src/train.py data/train`

#### 识别
`python3 src/predict.py trained_knn_model.clf data/test`



#### 准确率评估

初步结论：face-recognition已有模型的识别准确率，对西方人比东亚人要高。

https://github.com/ageitgey/face_recognition



##### 样本评估测试1（西方人）

```
name		total	correct	wrong	fail	precision	elapsed time
   3137953	4	4	0	0	1.000	0:00:00.787475
   3152605	13	12	0	1	0.923	0:00:02.270396
   3144303	8	7	1	0	0.875	0:00:01.505216
   3140568	5	4	0	1	0.800	0:00:00.787946
   3131124	13	13	0	0	1.000	0:00:02.414506
   3151489	21	15	3	3	0.714	0:00:03.452148
   3129791	8	8	0	0	1.000	0:00:01.514386
   3135437	12	11	0	1	0.917	0:00:02.086602
   3141312	7	7	0	0	1.000	0:00:01.301652
   3129067	7	7	0	0	1.000	0:00:01.295172
   3152983	12	10	0	2	0.833	0:00:01.930866
   3135911	16	14	0	2	0.875	0:00:02.667131
   3158751	7	6	0	1	0.857	0:00:01.144044
   3131306	12	10	1	1	0.833	0:00:02.088166
   3132111	11	11	0	0	1.000	0:00:02.047547
   3150050	23	22	0	1	0.957	0:00:04.128879
   3135079	8	7	0	1	0.875	0:00:01.330206
   3136962	23	22	1	0	0.957	0:00:04.301207
   3150133	12	11	0	2	0.917	0:00:02.080511
   3148464	10	10	0	0	1.000	0:00:01.874853
   3146486	10	8	2	0	0.800	0:00:01.860759
   3148185	14	14	0	0	1.000	0:00:02.610956
   3158974	18	18	0	0	1.000	0:00:03.345388
   3143135	9	8	0	1	0.889	0:00:01.568921
   3138464	10	7	0	3	0.700	0:00:01.391683
   3143506	29	25	0	4	0.862	0:00:04.769276
   3134589	13	13	0	0	1.000	0:00:02.413014
   3152330	7	7	0	0	1.000	0:00:01.306790
   3148203	19	18	0	1	0.947	0:00:03.391766
   3147720	5	5	0	0	1.000	0:00:00.935145
   3155377	6	5	1	0	0.833	0:00:01.119683
   3136088	8	6	0	2	0.750	0:00:01.188695
   3142219	6	6	0	0	1.000	0:00:01.116352
   3130829	8	7	0	1	0.875	0:00:01.332071

```

[人脸数据来源]: https://github.com/ZhaoJ9014/face.evoLVe.PyTorch#Data-Zoo	"CASIA-WebFace"



##### 样本评估测试1（东亚人）

```
name		total	correct	wrong	fail	precision	elapsed time
chenguanxi	44	9	0	35	0.205	0:00:01.956864
chenzhipeng	26	3	5	18	0.115	0:00:01.568268
chenweiting	47	7	1	39	0.149	0:00:01.813229
     baike	36	13	3	20	0.361	0:00:03.033239
     benxi	38	2	1	35	0.053	0:00:00.878513
changshilei	41	2	0	39	0.049	0:00:00.742862
  baibaihe	51	14	1	36	0.275	0:00:03.007897
  baobeier	30	13	1	16	0.433	0:00:02.557159
  daipeini	18	9	1	8	0.500	0:00:01.824227
   denglun	40	3	1	36	0.075	0:00:01.122187
chenqiaoen	47	12	2	33	0.255	0:00:02.764773
baijingting	36	4	1	31	0.111	0:00:01.169608
caobingkun	55	17	1	37	0.309	0:00:03.420065
  dengchao	21	8	1	12	0.381	0:00:01.648922
chenxuedong	38	5	1	32	0.132	0:00:01.367289
baojianfeng	51	18	1	32	0.353	0:00:03.526478
    chenhe	41	7	2	32	0.171	0:00:01.862193
      axin	22	7	0	15	0.318	0:00:01.347770
 changyuan	32	9	0	23	0.281	0:00:01.752277
  dilireba	52	15	1	36	0.288	0:00:03.051705
  chenlong	49	8	0	41	0.163	0:00:01.780610
chenfarong	43	8	3	32	0.186	0:00:02.206717
     aidai	36	7	4	25	0.194	0:00:02.113320
      anhu	47	12	1	34	0.255	0:00:02.537665
 caoyunjin	48	10	0	38	0.208	0:00:02.098453
   caoying	55	11	2	42	0.200	0:00:02.625822
chenhuilin	55	24	3	28	0.436	0:00:04.792539
 caihancen	28	2	3	23	0.071	0:00:01.096193
caizhuoyan	45	9	1	35	0.200	0:00:02.083759
cengyongti	53	16	0	37	0.302	0:00:03.091609
chenbailin	20	9	0	11	0.450	0:00:01.608893
dazhangwei	34	6	0	28	0.176	0:00:01.295548
chenhaomin	28	4	3	21	0.143	0:00:01.413220
   chenyao	59	8	8	43	0.136	0:00:03.158334
  dingding	4	0	1	3	0.000	0:00:00.197136
    chenyi	19	3	0	16	0.158	0:00:00.689696
 chenyufan	14	2	0	12	0.143	0:00:00.456303
   chenkun	27	6	0	21	0.222	0:00:01.251692
   chenshu	50	8	3	39	0.160	0:00:02.277763
 chenyixun	36	8	1	27	0.222	0:00:01.816514
 chenjiaqi	2	0	1	1	0.000	0:00:00.183639
chenderong	42	15	1	26	0.357	0:00:02.965833
 chenxiang	25	3	1	21	0.120	0:00:00.903731
 chenxinyu	49	14	4	31	0.286	0:00:03.336504
  dengziqi	34	7	0	27	0.206	0:00:01.469624
caiguoqing	33	9	0	24	0.273	0:00:01.785159
  caiyilin	34	9	4	21	0.265	0:00:02.394095
chenhuixian	35	2	0	33	0.057	0:00:00.739086
 chenglong	29	8	1	20	0.276	0:00:01.711095
chendouling	38	5	0	33	0.132	0:00:01.226902
```

[人脸数据来源]: https://github.com/X-zhangyang/Real-World-Masked-Face-Dataset	"RMFD"

