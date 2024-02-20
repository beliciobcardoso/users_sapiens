SELECT
    CASE modnam
        WHEN 'R' THEN 'MERCADO'
        WHEN 'S' THEN 'SUPRIMENTOS'
        WHEN 'F' THEN 'FINANÇAS'
        WHEN 'C' THEN 'CONTROLADORIA'
        ELSE 'LIVRE'
    END AS MODULOS,
    sec.numsec as ID_CONEXAO,
    CONVERT(
        VARCHAR, DATEADD(DAY, dattim, '1899-12-30'), 103
    ) + ' ' + RIGHT(
        '0' + CONVERT(
            VARCHAR, FLOOR(dattim % 1 * 24)
        ), 2
    ) + ':' + RIGHT(
        '0' + CONVERT(
            VARCHAR, FLOOR(dattim * 24 * 60) % 60
        ), 2
    ) AS DATA_CONEXAO,
    comnam AS NAME_SERVER,
    usrnam AS CONECT_SERVER,
    appnam AS NAME_APP,
    appusr AS CONECT_SAPIENS
FROM sapiens.dbo.r911sec AS sec
    FULL OUTER JOIN sapiens.dbo.r911mod AS modulo ON sec.numsec = modulo.numsec
WHERE
    appnam = 'SAPIENS';