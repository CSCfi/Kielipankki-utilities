<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="2.0">

<!--  <xsl:output indent="no" method="xml"/>-->
  <xsl:output method="xml" indent="no"  encoding="UTF-8"/>
  


<xsl:template match="KlK">
  <html>
    <body>
      <h2>List of authors</h2>
      <table border="1">
	<tr>
	  <th>author</th>
	  <th>title</th>
	  <th>year</th>
	  <th>lang</th>
	</tr>
	<xsl:for-each select="text">
	  <tr>
	    <td><xsl:value-of select="@author"/></td>
	    <td><xsl:value-of select="@title"/></td>
	    <td><xsl:value-of select="@year"/></td>
	    <td><xsl:value-of select="@lang"/></td>
	  </tr>
	</xsl:for-each>
      </table>
    </body>
  </html>
</xsl:template>


  

</xsl:stylesheet>
